from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rate_limit import rate_limit
from app.db.session import get_session
from app.models.email_verification import (
    EmailVerificationToken, 
    EmailVerificationRequest, 
    EmailVerificationResponse
)
from app.models.user import User
from sqlmodel import select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-verification", tags=["Email Verification"])


@router.post(
    "/verify",
    response_model=EmailVerificationResponse,
    dependencies=[Depends(rate_limit("email_verify", limit=10, window_seconds=60))],
)
def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_session)
):
    """
    Verify email using either token (from URL) or code (manual entry)
    """
    logger.info(f"Email verification attempt for: {request.email}")
    
    try:
        # Find user by email
        user = db.exec(select(User).where(User.email == request.email)).first()
        if not user:
            logger.warning(f"User not found for email: {request.email}")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Check if email is already verified
        if user.email_verified:
            logger.info(f"Email already verified for user: {request.email}")
            return EmailVerificationResponse(
                success=True,
                message="El email ya está verificado",
                verified=True
            )
        
        # Build query for verification token
        query = select(EmailVerificationToken).where(
            EmailVerificationToken.email == request.email,
            EmailVerificationToken.used_at.is_(None)
        )
        
        # Add token or code filter
        if request.token:
            query = query.where(EmailVerificationToken.token == request.token)
            logger.info(f"Verifying with token for: {request.email}")
        elif request.code:
            query = query.where(EmailVerificationToken.code == request.code)
            logger.info(f"Verifying with code for: {request.email}")
        else:
            logger.error(f"No token or code provided for: {request.email}")
            raise HTTPException(status_code=400, detail="Token o código requerido")
        
        verification_token = db.exec(query).first()
        
        if not verification_token:
            logger.warning(f"Invalid verification token/code for: {request.email}")
            raise HTTPException(status_code=400, detail="Token o código inválido")
        
        # Check if token is expired
        if verification_token.is_expired():
            logger.warning(f"Expired verification token for: {request.email}")
            raise HTTPException(status_code=400, detail="El token ha expirado")
        
        # Mark token as used
        verification_token.mark_as_used()
        db.add(verification_token)
        
        # Mark user email as verified
        user.email_verified = True
        user.email_verified_at = datetime.utcnow()
        db.add(user)
        
        db.commit()
        
        logger.info(f"Email successfully verified for: {request.email}")
        return EmailVerificationResponse(
            success=True,
            message="Email verificado exitosamente",
            verified=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email for {request.email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/resend",
    response_model=EmailVerificationResponse,
    dependencies=[Depends(rate_limit("email_resend", limit=5, window_seconds=60))],
)
def resend_verification_email(
    email: str,
    db: Session = Depends(get_session)
):
    """
    Resend verification email to user
    """
    logger.info(f"Resend verification email request for: {email}")
    
    try:
        # Find user by email
        user = db.exec(select(User).where(User.email == email)).first()
        if not user:
            logger.warning(f"User not found for resend request: {email}")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Check if email is already verified
        if user.email_verified:
            logger.info(f"Email already verified, no resend needed: {email}")
            return EmailVerificationResponse(
                success=True,
                message="El email ya está verificado",
                verified=True
            )
        
        # Trigger verification email
        from app.controllers.user_controller import trigger_verification_email
        trigger_verification_email(
            user_id=user.id,
            user_email=user.email,
            display_name=user.nombre or user.username or user.email.split('@')[0]
        )
        
        logger.info(f"Verification email resent to: {email}")
        return EmailVerificationResponse(
            success=True,
            message="Email de verificación enviado",
            verified=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending verification email to {email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/status/{email}", response_model=dict)
def get_verification_status(
    email: str,
    db: Session = Depends(get_session)
):
    """
    Get email verification status for a user
    """
    try:
        user = db.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "email": email,
            "verified": user.email_verified,
            "verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting verification status for {email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")