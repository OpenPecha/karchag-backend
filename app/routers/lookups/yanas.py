from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import Yana, User
from app.schemas import YanaResponse, YanaCreate
from app.dependencies.auth import require_admin
from datetime import datetime

router = APIRouter(prefix="/yanas", tags=["yanas"])

# ==================== PUBLIC ENDPOINTS ====================

@router.get("", response_model=List[YanaResponse])
async def get_yanas(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active yanas"""
    yanas = db.query(Yana).filter(
        Yana.is_active == True
    ).order_by(Yana.order_index).all()
    
    return yanas

# ==================== ADMIN ENDPOINTS ====================

@router.get("/all", tags=["Yana Management"])
async def get_all_yanas_admin(
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all yanas (including inactive) - Admin only"""
    yanas = db.query(Yana).order_by(Yana.order_index).all()
    return {"yanas": yanas}

@router.get("/{yana_id}/details", tags=["Yana Management"])
async def get_yana_detail_admin(
    yana_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific yana detail for editing - Admin only"""
    yana = db.query(Yana).filter(Yana.id == yana_id).first()
    if not yana:
        raise HTTPException(status_code=404, detail="Yana not found")
    
    return yana

@router.get("/{yana_id}", response_model=YanaResponse)
async def get_yana_detail(
    yana_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific yana detail"""
    yana = db.query(Yana).filter(
        Yana.id == yana_id,
        Yana.is_active == True
    ).first()
    
    if not yana:
        raise HTTPException(status_code=404, detail="Yana not found")
    
    return yana

@router.post("", response_model=YanaResponse, status_code=status.HTTP_201_CREATED, tags=["Yana Management"])
async def create_yana(
    yana_data: YanaCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new yana - Admin only"""
    yana = Yana(
        name_english=yana_data.name_english,
        name_tibetan=yana_data.name_tibetan
    )
    
    db.add(yana)
    db.commit()
    db.refresh(yana)
    
    return yana

@router.put("/{yana_id}", response_model=YanaResponse, tags=["Yana Management"])
async def update_yana(
    yana_id: int,
    yana_data: YanaCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update yana - Admin only"""
    yana = db.query(Yana).filter(Yana.id == yana_id).first()
    if not yana:
        raise HTTPException(status_code=404, detail="Yana not found")
    
    # Update fields
    update_data = yana_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(yana, field, value)
    
    db.commit()
    db.refresh(yana)
    
    return yana

@router.delete("/{yana_id}", tags=["Yana Management"])
async def delete_yana(
    yana_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete yana - Admin only"""
    yana = db.query(Yana).filter(Yana.id == yana_id).first()
    if not yana:
        raise HTTPException(status_code=404, detail="Yana not found")
    
    db.delete(yana)
    db.commit()
    
    return {"message": "Yana deleted successfully"}
