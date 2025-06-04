from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from database import get_db
from models import MainCategory, SubCategory, KangyurAudio, KagyurText
from schemas import MainCategoryResponse, SubCategoryResponse, AudioResponse, PaginatedResponse
import math

router = APIRouter()

@router.get("/categories")
async def get_audio_categories(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active main categories that have audio content"""
    categories = db.query(MainCategory).join(SubCategory).join(KagyurText).join(KangyurAudio).filter(
        MainCategory.is_active == True,
        SubCategory.is_active == True,
        KagyurText.is_active == True,
        KangyurAudio.is_active == True
    ).distinct().order_by(MainCategory.order_index).all()
    
    # Add audio counts for each category
    result = []
    for category in categories:
        audio_count = db.query(func.count(KangyurAudio.id)).join(KagyurText).join(SubCategory).filter(
            SubCategory.main_category_id == category.id,
            KangyurAudio.is_active == True
        ).scalar()
        
        category_dict = MainCategoryResponse.from_orm(category).dict()
        category_dict['audio_count'] = audio_count
        result.append(category_dict)
    
    return {"categories": result}

@router.get("/categories/{category_id}/subcategories")
async def get_audio_subcategories(
    category_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get sub-categories under specific category that have audio content"""
    subcategories = db.query(SubCategory).join(KagyurText).join(KangyurAudio).filter(
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True,
        KagyurText.is_active == True,
        KangyurAudio.is_active == True
    ).distinct().order_by(SubCategory.order_index).all()
    
    # Add audio counts for each subcategory
    result = []
    for subcategory in subcategories:
        audio_count = db.query(func.count(KangyurAudio.id)).join(KagyurText).filter(
            KagyurText.sub_category_id == subcategory.id,
            KangyurAudio.is_active == True
        ).scalar()
        
        subcategory_dict = SubCategoryResponse.from_orm(subcategory).dict()
        subcategory_dict['audio_count'] = audio_count
        result.append(subcategory_dict)
    
    return {"subcategories": result}

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/audio")
async def get_subcategory_audio(
    category_id: int,
    sub_category_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    narrator: Optional[str] = Query(None),
    quality: Optional[str] = Query(None),
    language: Optional[str] = Query(None, regex="^(tibetan|english)$"),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all audio files under a specific sub-category"""
    # Verify subcategory belongs to main category
    subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).first()
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    offset = (page - 1) * limit
    
    # Build query
    query = db.query(KangyurAudio).join(KagyurText).filter(
        KagyurText.sub_category_id == sub_category_id,
        KagyurText.is_active == True,
        KangyurAudio.is_active == True
    )
    
    # Apply filters
    if narrator:
        query = query.filter(
            (KangyurAudio.narrator_name_english.ilike(f"%{narrator}%")) |
            (KangyurAudio.narrator_name_tibetan.ilike(f"%{narrator}%"))
        )
    
    if quality:
        query = query.filter(KangyurAudio.audio_quality == quality)
    
    if language:
        query = query.filter(KangyurAudio.audio_language == language)
    
    total = query.count()
    audio_files = query.order_by(KangyurAudio.order_index).offset(offset).limit(limit).all()
    
    return PaginatedResponse(
        items=[AudioResponse.from_orm(audio).dict() for audio in audio_files],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit)
    )

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/audio/{audio_id}")
async def get_specific_audio(
    category_id: int,
    sub_category_id: int,
    audio_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific audio details and streaming URL"""
    audio = db.query(KangyurAudio).join(KagyurText).join(SubCategory).filter(
        KangyurAudio.id == audio_id,
        KagyurText.sub_category_id == sub_category_id,
        SubCategory.main_category_id == category_id,
        KangyurAudio.is_active == True
    ).first()
    
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return AudioResponse.from_orm(audio)