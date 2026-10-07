"""
Security utilities and authentication dependencies.
This module provides compatibility with the old authentication system
while using Firebase Auth as the primary authentication method.
"""

from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.core.auth_firebase import verify_firebase_token
from app.db.session import get_session
from app.controllers.user_controller import get_user_by_firebase_uid
from app.controllers.role_controller import user_has_role, get_user_roles
# Removed RoleType import - now using strings
from app.models.user import User
from typing import List


def get_current_user(firebase_user: dict = Depends(verify_firebase_token)):
    """
    Dependency to get the current authenticated user.
    This is a compatibility function that works with Firebase Auth.
    
    Args:
        firebase_user: The Firebase user data from the token verification
        
    Returns:
        dict: Firebase user data
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return firebase_user


def get_current_db_user(
    firebase_user: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user from the database.
    
    Args:
        firebase_user: The Firebase user data from the token verification
        db: Database session
        
    Returns:
        User: User object from database
        
    Raises:
        HTTPException: If user is not authenticated or not found in database
    """
    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = get_user_by_firebase_uid(db, firebase_user['uid'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database"
        )
    
    return user


def require_role(required_role: str):
    """
    Dependency factory to require a specific role.
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        Dependency function that checks for the required role
    """
    def check_role(
        current_user: User = Depends(get_current_db_user),
        db: Session = Depends(get_session)
    ):
        if not user_has_role(db, current_user.id, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    
    return check_role


def require_admin():
    """Dependency to require admin role"""
    return require_role("admin")


def require_manager_or_admin():
    """Dependency to require manager or admin role"""
    def check_role(
        current_user: User = Depends(get_current_db_user),
        db: Session = Depends(get_session)
    ):
        if not (user_has_role(db, current_user.id, "admin") or 
                user_has_role(db, current_user.id, "manager")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or Manager role required"
            )
        return current_user
    
    return check_role


def get_user_permissions(user: User, db: Session) -> List[str]:
    """
    Get all roles/permissions for a user.
    
    Args:
        user: User object
        db: Database session
        
    Returns:
        List of roles the user has
    """
    roles = get_user_roles(db, user.id)
    return [role.name for role in roles]


# Alias for backward compatibility
get_current_active_user = get_current_user


def is_admin_user(user_data: dict, session: Session) -> bool:
    """Check if the firebase user has admin role in database"""
    uid = user_data.get("uid")
    if not uid:
        return False
    user = get_user_by_firebase_uid(session, uid)
    if not user:
        return False
    return user_has_role(session, user.id, "admin")


def check_order_ownership_or_admin(order, user_data: dict, session: Session) -> bool:
    """Verifies that the user owns the order via customer email or has admin role"""
    if is_admin_user(user_data, session):
        return True
    from app.models.customer import Customer
    customer = session.get(Customer, order.customer_id)
    if customer and customer.email and customer.email.lower() == (user_data.get("email") or "").lower():
        return True
    raise HTTPException(status_code=403, detail="No autorizado para acceder a esta orden")
