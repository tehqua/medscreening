"""
File handling service with upload, validation, and cleanup.
"""

from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import uuid
import os
import logging
import aiofiles
from datetime import datetime, timedelta
from typing import List, Optional
import magic  # python-magic for file type detection
import hashlib

logger = logging.getLogger(__name__)


async def save_uploaded_file(
    file: UploadFile,
    upload_dir: str,
    file_type: str,
    allowed_extensions: List[str],
    max_size_mb: int
) -> str:
    """
    Save uploaded file with validation and security checks.
    
    Args:
        file: Uploaded file
        upload_dir: Directory to save file
        file_type: Type of file (image/audio)
        allowed_extensions: List of allowed extensions
        max_size_mb: Maximum file size in MB
        
    Returns:
        Path to saved file
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        # Create upload directory if not exists
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large ({file_size_mb:.1f}MB). Maximum size: {max_size_mb}MB"
            )
        
        # Validate file is not empty
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        # Validate actual file type using magic numbers
        try:
            mime_type = magic.from_buffer(content, mime=True)
            
            # Validate MIME type matches file type
            if file_type == "image" and not mime_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File is not an image. Detected type: {mime_type}"
                )
            elif file_type == "audio" and not mime_type.startswith("audio/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File is not an audio file. Detected type: {mime_type}"
                )
        except Exception as e:
            logger.warning(f"Could not detect MIME type: {e}")
            # Continue without MIME validation if magic fails
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file_id}{ext}"
        
        # Sanitize filename (remove any path traversal attempts)
        filename = os.path.basename(filename)
        
        # Full file path
        file_path = os.path.join(upload_dir, filename)
        
        # Save file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        # Calculate file hash for integrity
        file_hash = hashlib.sha256(content).hexdigest()
        
        logger.info(
            f"File saved: {filename} ({file_size_mb:.2f}MB, "
            f"hash: {file_hash[:16]}...)"
        )
        
        return file_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


async def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


async def cleanup_old_files(upload_dir: str, days_old: int = 7):
    """
    Clean up files older than specified days.
    
    Args:
        upload_dir: Directory containing uploaded files
        days_old: Delete files older than this many days
    """
    try:
        upload_path = Path(upload_dir)
        if not upload_path.exists():
            return
        
        cutoff_time = datetime.utcnow() - timedelta(days=days_old)
        deleted_count = 0
        
        for file_path in upload_path.iterdir():
            if file_path.is_file():
                # Get file modification time
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting old file {file_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old files from {upload_dir}")
            
    except Exception as e:
        logger.error(f"Error in cleanup_old_files: {e}", exc_info=True)


async def get_file_info(file_path: str) -> dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    try:
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        stat = os.stat(file_path)
        
        return {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return {"error": str(e)}


def validate_file_path(file_path: str, upload_dir: str) -> bool:
    """
    Validate that file path is within upload directory (prevent path traversal).
    
    Args:
        file_path: File path to validate
        upload_dir: Base upload directory
        
    Returns:
        True if path is safe
    """
    try:
        # Resolve absolute paths
        abs_file_path = os.path.abspath(file_path)
        abs_upload_dir = os.path.abspath(upload_dir)
        
        # Check if file is within upload directory
        return abs_file_path.startswith(abs_upload_dir)
    except Exception:
        return False