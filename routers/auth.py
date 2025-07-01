from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import get_db
from models import User
from schemas import LoginRequest, LoginResponse, RefreshResponse, LogoutResponse
from dependencies.auth import get_current_user, get_refresh_token_user
from core.security import  create_access_token
from utils.audit import log_activity
from services.auth_service.handle_signup import handle_signup
from services.auth_service.handle_login import handle_login

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=LoginResponse)
async def signup(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    ip = request.client.host
    return await handle_signup(data, db, ip_address=ip)
    """Register a new user and return JWT tokens"""


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    return await handle_login(request=request,login_data=login_data,db=db)
    
    

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

