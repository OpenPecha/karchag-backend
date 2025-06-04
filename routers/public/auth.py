from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import get_db
from models import User
from schemas import LoginRequest, LoginResponse, RefreshResponse, LogoutResponse
from core.dependencies import get_current_user, get_refresh_token_user
from core.security import verify_password, create_access_token, create_refresh_token
from utils.audit import log_activity

router = APIRouter( tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    
    # Find user by username or email
    user = db.query(User).filter(
        and_(
            (User.username == login_data.username) | (User.email == login_data.username),
            User.is_active == True
        )
    ).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Prepare user data for token creation
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }
    
    # Generate tokens
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)
    
    # Log successful login
    log_activity(
        db=db,
        user_id=user.id,
        table_name="USERS",
        record_id=user.id,
        action="LOGIN",
        ip_address=request.client.host
    )
    
    return LoginResponse(
        message="Login successful",
        user=user,
        tokens={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600  # 1 hour in seconds
        }
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    user: User = Depends(get_refresh_token_user)
):
    """Refresh access token using refresh token"""
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }
    
    # Generate new access token
    new_access_token = create_access_token(user_data)
    
    return RefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=3600
    )

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and log activity"""
    
    # Log logout activity
    log_activity(
        db=db,
        user_id=current_user.id,
        table_name="USERS",
        record_id=current_user.id,
        action="LOGOUT",
        ip_address=request.client.host
    )
    
    return LogoutResponse(message="Logout successful")

