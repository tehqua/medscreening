"""
Authentication and authorization utilities.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from .config import get_settings, Settings
from .schemas import TokenData
from .database import get_db, Database

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def create_access_token(
    data: dict,
    settings: Settings,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Token payload data
        settings: Application settings
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt


def verify_token(token: str, settings: Settings) -> TokenData:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token
        settings: Application settings
        
    Returns:
        Token data
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        
        patient_id: str = payload.get("patient_id")
        session_id: str = payload.get("session_id")
        
        if patient_id is None or session_id is None:
            raise credentials_exception
        
        return TokenData(patient_id=patient_id, session_id=session_id)
        
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
    db: Database = Depends(get_db)
) -> TokenData:
    """
    Get current authenticated user from token.
    
    This dependency verifies the JWT token and validates the session.
    
    Args:
        credentials: HTTP authorization credentials
        settings: Application settings
        db: Database instance
        
    Returns:
        Token data with patient_id and session_id
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    token_data = verify_token(token, settings)
    
    # Verify session is still valid
    session = await db.get_session(token_data.session_id)
    
    if not session or not session.get("active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extend session on activity
    await db.extend_session(
        token_data.session_id,
        minutes=settings.SESSION_EXPIRE_MINUTES
    )
    
    return token_data


def validate_patient_id(patient_id: str) -> bool:
    """
    Validate patient ID format.
    
    Expected format: FirstName###_LastName###_uuid
    Example: Adam631_Cronin387_aff8f143-2375-416f-901d-b0e4c73e3e58
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        True if valid
    """
    import re
    
    # Pattern: Name###_Name###_uuid
    pattern = r'^[A-Z][a-z]+\d+_[A-Z][a-z]+\d+_[a-f0-9-]{36}$'
    
    return bool(re.match(pattern, patient_id))