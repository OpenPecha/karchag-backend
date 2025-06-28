from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from typing import Optional
from models import User
from sqlalchemy import and_
from database import get_db
from sqlalchemy.orm import Session
from core.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials, "access")
    user_id = int(payload.get("sub"))
    
    user = db.query(User).filter(
        and_(User.id == user_id, User.is_active == True)
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin privileges"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_current_user_optional() -> Optional[dict]:
    """Get current user if authenticated, None otherwise"""
    # Optional authentication for public endpoints that show different data for admins
    try:
        return await get_current_user()
    except:
        return None
    
async def get_refresh_token_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get user from refresh token"""
    payload = verify_token(credentials.credentials, "refresh")
    user_id = int(payload.get("sub"))
    
    user = db.query(User).filter(
        and_(User.id == user_id, User.is_active == True)
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user