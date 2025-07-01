from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from models import Sermon, User
from schemas import SermonResponse, SermonCreate
from dependencies.auth import require_admin
from datetime import datetime

router = APIRouter()

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/sermons", response_model=List[SermonResponse])
async def get_sermons(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active sermons"""
    sermons = db.query(Sermon).filter(
        Sermon.is_active == True
    ).order_by(Sermon.order_index).all()
    
    return sermons

@router.get("/sermons/{sermon_id}", response_model=SermonResponse)
async def get_sermon_detail(
    sermon_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific sermon detail"""
    sermon = db.query(Sermon).filter(
        Sermon.id == sermon_id,
        Sermon.is_active == True
    ).first()
    
    if not sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    
    return sermon

# ==================== ADMIN ENDPOINTS ====================

@router.get("/sermons/all", tags=["Sermon Management"])
async def get_all_sermons_admin(
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all sermons (including inactive) - Admin only"""
    sermons = db.query(Sermon).order_by(Sermon.order_index).all()
    return {"sermons": sermons}

@router.get("/sermons/{sermon_id}/details", tags=["Sermon Management"])
async def get_sermon_detail_admin(
    sermon_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific sermon detail for editing - Admin only"""
    sermon = db.query(Sermon).filter(Sermon.id == sermon_id).first()
    if not sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    
    return sermon

@router.post("/sermons", response_model=SermonResponse, status_code=status.HTTP_201_CREATED, tags=["Sermon Management"])
async def create_sermon(
    sermon_data: SermonCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new sermon - Admin only"""
    sermon = Sermon(
        name_english=sermon_data.name_english,
        name_tibetan=sermon_data.name_tibetan
    )
    
    db.add(sermon)
    db.commit()
    db.refresh(sermon)
    
    return sermon

@router.put("/sermons/{sermon_id}", response_model=SermonResponse, tags=["Sermon Management"])
async def update_sermon(
    sermon_id: int,
    sermon_data: SermonCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update sermon - Admin only"""
    sermon = db.query(Sermon).filter(Sermon.id == sermon_id).first()
    if not sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    
    # Update fields
    update_data = sermon_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sermon, field, value)
    
    db.commit()
    db.refresh(sermon)
    
    return sermon

@router.delete("/sermons/{sermon_id}", tags=["Sermon Management"])
async def delete_sermon(
    sermon_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete sermon - Admin only"""
    sermon = db.query(Sermon).filter(Sermon.id == sermon_id).first()
    if not sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    
    db.delete(sermon)
    db.commit()
    
    return {"message": "Sermon deleted successfully"}
