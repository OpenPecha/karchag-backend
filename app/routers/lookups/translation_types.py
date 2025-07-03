from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from models import TranslationType, User
from schemas import TranslationTypeResponse, TranslationTypeCreate
from dependencies.auth import require_admin
from datetime import datetime

router = APIRouter(prefix="/translation-types", tags=["translation-types"])

# ==================== PUBLIC ENDPOINTS ====================

@router.get("", response_model=List[TranslationTypeResponse])
async def get_translation_types(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active translation types"""
    translation_types = db.query(TranslationType).filter(
        TranslationType.is_active == True
    ).order_by(TranslationType.order_index).all()
    
    return translation_types

@router.get("/{type_id}/", response_model=TranslationTypeResponse)
async def get_translation_type_detail(
    type_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific translation type detail"""
    translation_type = db.query(TranslationType).filter(
        TranslationType.id == type_id,
        TranslationType.is_active == True
    ).first()
    
    if not translation_type:
        raise HTTPException(status_code=404, detail="Translation type not found")
    
    return translation_type

# ==================== ADMIN ENDPOINTS ====================

@router.get("/all", tags=["Translation Type Management"])
async def get_all_translation_types_admin(
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all translation types (including inactive) - Admin only"""
    translation_types = db.query(TranslationType).order_by(TranslationType.order_index).all()
    return {"translation_types": translation_types}

@router.get("/{type_id}/details", tags=["Translation Type Management"])
async def get_translation_type_detail_admin(
    type_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific translation type detail for editing - Admin only"""
    translation_type = db.query(TranslationType).filter(TranslationType.id == type_id).first()
    if not translation_type:
        raise HTTPException(status_code=404, detail="Translation type not found")
    
    return translation_type

@router.post("/", response_model=TranslationTypeResponse, status_code=status.HTTP_201_CREATED, tags=["Translation Type Management"])
async def create_translation_type(
    type_data: TranslationTypeCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new translation type - Admin only"""
    translation_type = TranslationType(
        name_english=type_data.name_english,
        name_tibetan=type_data.name_tibetan
    )
    
    db.add(translation_type)
    db.commit()
    db.refresh(translation_type)
    
    return translation_type

@router.put("/{type_id}", response_model=TranslationTypeResponse, tags=["Translation Type Management"])
async def update_translation_type(
    type_id: int,
    type_data: TranslationTypeCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update translation type - Admin only"""
    translation_type = db.query(TranslationType).filter(TranslationType.id == type_id).first()
    if not translation_type:
        raise HTTPException(status_code=404, detail="Translation type not found")
    
    # Update fields
    update_data = type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(translation_type, field, value)
    
    db.commit()
    db.refresh(translation_type)
    
    return translation_type

@router.delete("/{type_id}", tags=["Translation Type Management"])
async def delete_translation_type(
    type_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete translation type - Admin only"""
    translation_type = db.query(TranslationType).filter(TranslationType.id == type_id).first()
    if not translation_type:
        raise HTTPException(status_code=404, detail="Translation type not found")
    
    db.delete(translation_type)
    db.commit()
    
    return {"message": "Translation type deleted successfully"}
