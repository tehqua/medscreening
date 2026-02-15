"""
Authentication router.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
import uuid
import logging

from ..config import get_settings, Settings
from ..database import get_db, Database
from ..schemas import LoginRequest, LoginResponse
from ..auth import create_access_token, validate_patient_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    settings: Settings = Depends(get_settings),
    db: Database = Depends(get_db)
):
    """
    Authenticate patient and create session.
    
    This endpoint validates the patient ID and creates a new session
    with an access token for subsequent API calls.
    
    Args:
        request: Login request with patient_id
        settings: Application settings
        db: Database instance
        
    Returns:
        Login response with access token and session info
        
    Raises:
        HTTPException: If patient ID is invalid
    """
    patient_id = request.patient_id
    
    # Validate patient ID format
    if not validate_patient_id(patient_id):
        logger.warning(f"Invalid patient ID format: {patient_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid patient ID format"
        )
    
    # In production, verify patient exists in database here
    # For now, we accept any valid-format patient ID
    
    # Create session
    session_id = str(uuid.uuid4())
    
    await db.create_session(
        session_id=session_id,
        patient_id=patient_id,
        expires_in_minutes=settings.SESSION_EXPIRE_MINUTES
    )
    
    logger.info(f"Session created for patient: {patient_id}")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"patient_id": patient_id, "session_id": session_id},
        settings=settings,
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        session_id=session_id,
        patient_id=patient_id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    )


@router.post("/logout")
async def logout(
    session_id: str,
    db: Database = Depends(get_db)
):
    """
    Logout and invalidate session.
    
    Args:
        session_id: Session identifier
        db: Database instance
        
    Returns:
        Logout confirmation
    """
    await db.invalidate_session(session_id)
    logger.info(f"Session invalidated: {session_id}")
    
    return {"message": "Logged out successfully"}