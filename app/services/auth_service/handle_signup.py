# app/services/auth_service.py

from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import LoginRequest, LoginResponse
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.utils.audit import log_activity

async def handle_signup(user_data: LoginRequest, db: Session, ip_address: str) -> LoginResponse:
    """Handles user signup and token generation"""

    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    password = hash_password(user_data.password)
    # Create and insert user
    new_user = User(
        username=user_data.username,
        email=user_data.username,
        hashed_password=password,
        is_active=True,
        is_admin=False,
        last_login=datetime.now(timezone.utc),
        
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(new_user)

    # Token payload
    payload = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_admin": new_user.is_admin
    }

    # Generate JWT tokens
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    # Log activity
    log_activity(
        db=db,
        user_id=new_user.id,
        table_name="USERS",
        record_id=new_user.id,
        action="SIGNUP",
        ip_address=ip_address
    )

    return LoginResponse(
        message="Signup successful",
        user=new_user,
        tokens={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    )