# app/routers/admin/lookups.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Sermon, Yana, TranslationType
from schemas import (
    SermonResponse, SermonCreate,
    YanaResponse, YanaCreate,
    TranslationTypeResponse, TranslationTypeCreate
)

router = APIRouter(tags=["Admin - Lookups"])

# SERMONS
@router.get("/sermons", response_model=List[SermonResponse])
async def get_all_sermons(db: Session = Depends(get_db)):
    """Get all sermons (active and inactive)"""
    sermons = db.query(Sermon).order_by(Sermon.order_index).all()
    return sermons

@router.post("/sermons", response_model=SermonResponse, status_code=201)
async def create_sermon(
    sermon_data: SermonCreate,
    db: Session = Depends(get_db)
):
    """Create a new sermon"""
    db_sermon = Sermon(**sermon_data.model_dump())
    db.add(db_sermon)
    db.commit()
    db.refresh(db_sermon)
    return db_sermon

@router.put("/sermons/{sermon_id}", response_model=SermonResponse)
async def update_sermon(
    sermon_id: int,
    sermon_data: SermonCreate,
    db: Session = Depends(get_db)
):
    """Update a sermon"""
    db_sermon = db.query(Sermon).filter(Sermon.id == sermon_id).first()
    if not db_sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    
    for field, value in sermon_data.model_dump().items():
        setattr(db_sermon, field, value)
    
    db.commit()
    db.refresh(db_sermon)
    return db_sermon

@router.delete("/sermons/{sermon_id}")
async def delete_sermon(sermon_id: int, db: Session = Depends(get_db)):
    """Delete a sermon"""
    db_sermon = db.query(Sermon).filter(Sermon.id == sermon_id).first()
    if not db_sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    
    db.delete(db_sermon)
    db.commit()
    return {"message": "Sermon deleted successfully"}

# YANAS
@router.get("/yanas", response_model=List[YanaResponse])
async def get_all_yanas(db: Session = Depends(get_db)):
    """Get all yanas (active and inactive)"""
    yanas = db.query(Yana).order_by(Yana.order_index).all()
    return yanas

@router.post("/yanas", response_model=YanaResponse, status_code=201)
async def create_yana(
    yana_data: YanaCreate,
    db: Session = Depends(get_db)
):
    """Create a new yana"""
    db_yana = Yana(**yana_data.model_dump())
    db.add(db_yana)
    db.commit()
    db.refresh(db_yana)
    return db_yana

@router.put("/yanas/{yana_id}", response_model=YanaResponse)
async def update_yana(
    yana_id: int,
    yana_data: YanaCreate,
    db: Session = Depends(get_db)
):
    """Update a yana"""
    db_yana = db.query(Yana).filter(Yana.id == yana_id).first()
    if not db_yana:
        raise HTTPException(status_code=404, detail="Yana not found")
    
    for field, value in yana_data.model_dump().items():
        setattr(db_yana, field, value)
    
    db.commit()
    db.refresh(db_yana)
    return db_yana

@router.delete("/yanas/{yana_id}")
async def delete_yana(yana_id: int, db: Session = Depends(get_db)):
    """Delete a yana"""
    db_yana = db.query(Yana).filter(Yana.id == yana_id).first()
    if not db_yana:
        raise HTTPException(status_code=404, detail="Yana not found")
    
    db.delete(db_yana)
    db.commit()
    return {"message": "Yana deleted successfully"}

# TRANSLATION TYPES
@router.get("/translation-types", response_model=List[TranslationTypeResponse])
async def get_all_translation_types(db: Session = Depends(get_db)):
    """Get all translation types (active and inactive)"""
    translation_types = db.query(TranslationType).order_by(TranslationType.order_index).all()
    return translation_types

@router.post("/translation-types", response_model=TranslationTypeResponse, status_code=201)
async def create_translation_type(
    translation_type_data: TranslationTypeCreate,
    db: Session = Depends(get_db)
):
    """Create a new translation type"""
    db_translation_type = TranslationType(**translation_type_data.model_dump())
    db.add(db_translation_type)
    db.commit()
    db.refresh(db_translation_type)
    return db_translation_type

@router.put("/translation-types/{translation_type_id}", response_model=TranslationTypeResponse)
async def update_translation_type(
    translation_type_id: int,
    translation_type_data: TranslationTypeCreate,
    db: Session = Depends(get_db)
):
    """Update a translation type"""
    db_translation_type = db.query(TranslationType).filter(
        TranslationType.id == translation_type_id
    ).first()
    if not db_translation_type:
        raise HTTPException(status_code=404, detail="Translation type not found")
    
    for field, value in translation_type_data.model_dump().items():
        setattr(db_translation_type, field, value)
    
    db.commit()
    db.refresh(db_translation_type)
    return db_translation_type

@router.delete("/translation-types/{translation_type_id}")
async def delete_translation_type(translation_type_id: int, db: Session = Depends(get_db)):
    """Delete a translation type"""
    db_translation_type = db.query(TranslationType).filter(
        TranslationType.id == translation_type_id
    ).first()
    if not db_translation_type:
        raise HTTPException(status_code=404, detail="Translation type not found")
    
    db.delete(db_translation_type)
    db.commit()
    return {"message": "Translation type deleted successfully"}