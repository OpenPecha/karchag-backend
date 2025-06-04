from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserUpdate, UserResponse, PaginatedUsersResponse
from core.dependencies import get_current_admin_user
from core.security import hash_password
from utils.audit import log_activity

router = APIRouter(
     tags=["User Management"])

@router.get("/users", response_model=PaginatedUsersResponse)
async def get_users(
    page: int = 1,
    limit: int = 20,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with pagination (Admin only)"""
    
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(User).count()
    
    # Get users with pagination
    users = db.query(User).offset(offset).limit(limit).all()
    
    return PaginatedUsersResponse(
        users=users,
        pagination={
            "current_page": page,
            "per_page": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only)"""
    
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=user_data.is_active,
        is_admin=user_data.is_admin
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_admin.id,
        table_name="USERS",
        record_id=new_user.id,
        action="CREATE",
        ip_address=Request.client.host
    )
    
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update an existing user (Admin only)"""
    
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.username:
        db_user.username = user_update.username
    if user_update.email:
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = hash_password(user_update.password)
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    if user_update.is_admin is not None:
        db_user.is_admin = user_update.is_admin
    
    db.commit()
    db.refresh(db_user)
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_admin.id,
        table_name="USERS",
        record_id=db_user.id,
        action="UPDATE",
        ip_address=Request.client.host
    )
    
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (Admin only)"""
    
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_admin.id,
        table_name="USERS",
        record_id=user_id,
        action="DELETE",
        ip_address=Request.client.host
    )
    
    return {"detail": "User deleted successfully"}