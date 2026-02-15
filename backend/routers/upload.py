"""
File upload router with validation and error handling.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Optional
import logging
from datetime import datetime

from ..schemas import FileUploadResponse
from ..services.file_service import save_uploaded_file, get_file_info, validate_file_path
from ..config import get_settings, Settings
from ..auth import get_current_user, TokenData
from ..validators import FileValidator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/image", response_model=FileUploadResponse)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    current_user: TokenData = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    Upload an image file.
    
    Accepts image files for skin condition analysis. The uploaded file
    will be validated for type, size, and content before saving.
    
    Supported formats: JPG, JPEG, PNG, GIF, WEBP
    Maximum size: 10MB (configurable)
    
    Args:
        file: Image file to upload
        current_user: Authenticated user
        settings: Application settings
        
    Returns:
        File upload response with file details
        
    Raises:
        HTTPException: If validation fails or upload error occurs
    """
    logger.info(
        f"Image upload request from patient {current_user.patient_id}: "
        f"{file.filename} ({file.content_type})"
    )
    
    try:
        # Validate filename
        is_valid, error = FileValidator.validate_file_extension(
            file.filename,
            "image"
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Validate content type
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {file.content_type}. Expected image/*"
            )
        
        # Save file
        file_path = await save_uploaded_file(
            file=file,
            upload_dir=settings.UPLOAD_DIR,
            file_type="image",
            allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS,
            max_size_mb=settings.MAX_FILE_SIZE_MB
        )
        
        # Get file info
        file_info = await get_file_info(file_path)
        
        logger.info(
            f"Image uploaded successfully: {file_path} "
            f"({file_info.get('size_mb', 0):.2f}MB)"
        )
        
        return FileUploadResponse(
            file_id=str(hash(file_path)),
            filename=file.filename,
            file_path=file_path,
            file_type="image",
            size_bytes=file_info.get("size_bytes", 0),
            uploaded_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/audio", response_model=FileUploadResponse)
async def upload_audio(
    file: UploadFile = File(..., description="Audio file to upload"),
    current_user: TokenData = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    Upload an audio file.
    
    Accepts audio files for speech-to-text transcription. The uploaded
    file will be validated for type, size, and content before saving.
    
    Supported formats: WAV, MP3, M4A, OGG
    Maximum size: 50MB (configurable)
    Recommended: WAV, 16kHz, mono
    
    Args:
        file: Audio file to upload
        current_user: Authenticated user
        settings: Application settings
        
    Returns:
        File upload response with file details
        
    Raises:
        HTTPException: If validation fails or upload error occurs
    """
    logger.info(
        f"Audio upload request from patient {current_user.patient_id}: "
        f"{file.filename} ({file.content_type})"
    )
    
    try:
        # Validate filename
        is_valid, error = FileValidator.validate_file_extension(
            file.filename,
            "audio"
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Validate content type
        if file.content_type and not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {file.content_type}. Expected audio/*"
            )
        
        # Save file
        file_path = await save_uploaded_file(
            file=file,
            upload_dir=settings.UPLOAD_DIR,
            file_type="audio",
            allowed_extensions=settings.ALLOWED_AUDIO_EXTENSIONS,
            max_size_mb=settings.MAX_FILE_SIZE_MB
        )
        
        # Get file info
        file_info = await get_file_info(file_path)
        
        logger.info(
            f"Audio uploaded successfully: {file_path} "
            f"({file_info.get('size_mb', 0):.2f}MB)"
        )
        
        return FileUploadResponse(
            file_id=str(hash(file_path)),
            filename=file.filename,
            file_path=file_path,
            file_type="audio",
            size_bytes=file_info.get("size_bytes", 0),
            uploaded_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio: {str(e)}"
        )


@router.get("/info/{file_id}")
async def get_upload_info(
    file_id: str,
    current_user: TokenData = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    Get information about an uploaded file.
    
    Retrieves metadata for a previously uploaded file including size,
    type, and upload timestamp.
    
    Args:
        file_id: File identifier (hash of file path)
        current_user: Authenticated user
        settings: Application settings
        
    Returns:
        File information dictionary
        
    Raises:
        HTTPException: If file not found
    """
    # Note: In production, you'd want to store file_id -> file_path mapping
    # in database and validate user owns the file
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File info endpoint not yet implemented. Use file_path from upload response."
    )


@router.delete("/{file_id}")
async def delete_upload(
    file_id: str,
    current_user: TokenData = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    Delete an uploaded file.
    
    Removes a previously uploaded file from storage. Users can only
    delete their own files.
    
    Args:
        file_id: File identifier
        current_user: Authenticated user
        settings: Application settings
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If file not found or unauthorized
    """
    # Note: In production, you'd want to:
    # 1. Look up file_path from database using file_id
    # 2. Verify current_user owns the file
    # 3. Delete from storage
    # 4. Remove from database
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File deletion endpoint not yet implemented."
    )


@router.get("/limits")
async def get_upload_limits(
    settings: Settings = Depends(get_settings)
):
    """
    Get upload size limits and allowed formats.
    
    Returns configuration for file uploads including maximum sizes
    and allowed extensions for each file type.
    
    Args:
        settings: Application settings
        
    Returns:
        Upload limits and allowed formats
    """
    return {
        "image": {
            "max_size_mb": settings.MAX_FILE_SIZE_MB,
            "allowed_extensions": settings.ALLOWED_IMAGE_EXTENSIONS,
            "mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"]
        },
        "audio": {
            "max_size_mb": settings.MAX_FILE_SIZE_MB,
            "allowed_extensions": settings.ALLOWED_AUDIO_EXTENSIONS,
            "mime_types": ["audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg"],
            "recommendations": {
                "format": "WAV",
                "sample_rate": "16kHz",
                "channels": "mono"
            }
        }
    }