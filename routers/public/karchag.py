from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from typing import List, Optional
from database import get_db
from models import MainCategory, SubCategory, KagyurText, TextSummary, YesheDESpan, Volume, KangyurAudio
from schemas import (
    MainCategoryResponse, MainCategoryWithSubCategories, MainCategoryCreate,
    SubCategoryResponse, SubCategoryWithTexts, SubCategoryCreate,
    KagyurTextResponse, KagyurTextCreate, AudioResponse
)

router = APIRouter()

# GET Endpoints
@router.get("/categories", response_model=List[MainCategoryWithSubCategories], tags=["Categories"])
async def get_categories(
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all main categories with their sub-categories.
    
    Args:
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        Hierarchical category structure with all active main categories and their sub-categories
    """
    categories = db.query(MainCategory).options(
        joinedload(MainCategory.sub_categories.and_(SubCategory.is_active == True))
    ).filter(
        MainCategory.is_active == True
    ).order_by(MainCategory.order_index).all()
    
    return categories

@router.get("/categories/{category_id}/subcategories", response_model=List[SubCategoryResponse], tags=["Sub-Categories"])
async def get_subcategories(
    category_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all sub-categories under a specific main category.
    
    Args:
        category_id: The ID of the main category
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        List of sub-categories with their basic info
    
    Raises:
        HTTPException: 404 if main category not found
    """
    # Verify main category exists
    category = db.query(MainCategory).filter(
        MainCategory.id == category_id,
        MainCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    sub_categories = db.query(SubCategory).filter(
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).order_by(SubCategory.order_index).all()
    
    return sub_categories

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/texts", tags=["Texts"])
async def get_texts(
    category_id: int,
    sub_category_id: int,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all texts under a specific sub-category with pagination.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category
        page: Page number (starts from 1)
        limit: Number of items per page (max 100)
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        Paginated list of texts with basic info
    
    Raises:
        HTTPException: 404 if sub-category not found
    """
    # Verify sub-category exists and belongs to the category
    sub_category = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).first()
    
    if not sub_category:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get total count
    total_count = db.query(func.count(KagyurText.id)).filter(
        KagyurText.sub_category_id == sub_category_id,
        KagyurText.is_active == True
    ).scalar()
    
    # Get paginated texts
    texts = db.query(KagyurText).filter(
        KagyurText.sub_category_id == sub_category_id,
        KagyurText.is_active == True
    ).order_by(KagyurText.order_index).offset(offset).limit(limit).all()
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "texts": texts,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_count,
            "items_per_page": limit,
            "has_next": has_next,
            "has_prev": has_prev
        }
    }

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/texts/{text_id}",
            response_model=KagyurTextResponse, tags=["Texts"])
async def get_text(
    category_id: int,
    sub_category_id: int,
    text_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve detailed information about a specific text.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category
        text_id: The ID of the text to retrieve
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        Complete text details including summary, volumes, and audio files
    
    Raises:
        HTTPException: 404 if text not found or doesn't belong to the hierarchy
    """
    # Verify the text exists and belongs to the correct hierarchy with eager loading
    text = db.query(KagyurText).options(
        joinedload(KagyurText.text_summary),
        joinedload(KagyurText.sermon),
        joinedload(KagyurText.yana),
        joinedload(KagyurText.translation_type),
        joinedload(KagyurText.yeshe_de_spans).joinedload(YesheDESpan.volumes),
        joinedload(KagyurText.audio_files)  # Assuming you have audio relationship
    ).join(SubCategory).filter(
        KagyurText.id == text_id,
        KagyurText.sub_category_id == sub_category_id,
        SubCategory.main_category_id == category_id,
        KagyurText.is_active == True
    ).first()
    
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    return text

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/texts/{text_id}/audio", tags=["Audio"])
async def get_text_audio(
    category_id: int,
    sub_category_id: int,
    text_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    quality: Optional[str] = Query(None, regex="^(128kbps|320kbps)$"),
    db: Session = Depends(get_db)
):
    """Get all audio files for a specific text"""
    # Verify the text exists and belongs to the specified category/subcategory
    text = db.query(KagyurText).filter(
        KagyurText.id == text_id,
        KagyurText.sub_category_id == sub_category_id
    ).first()
    
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    # Verify subcategory belongs to main category
    subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Invalid category/subcategory combination")
    
    # Build query for audio files
    query = db.query(KangyurAudio).filter(
        KangyurAudio.text_id == text_id,
        KangyurAudio.is_active == True
    )
    
    # Apply quality filter if specified
    if quality:
        query = query.filter(KangyurAudio.audio_quality == quality)
    
    audio_files = query.order_by(KangyurAudio.order_index).all()
    
    return {"audio_files": [AudioResponse.model_validate(audio) for audio in audio_files]}

@router.get("/audio/{audio_id}", tags=["Audio"])
async def get_audio_details(
    audio_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific audio file details and streaming URL"""
    audio = db.query(KangyurAudio).filter(
        KangyurAudio.id == audio_id,
        KangyurAudio.is_active == True
    ).first()
    
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return AudioResponse.model_validate(audio)