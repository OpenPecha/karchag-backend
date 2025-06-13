from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func,and_, or_
from typing import List, Optional
from database import get_db
from models import MainCategory, SubCategory, KagyurText, TextSummary, YesheDESpan, Volume, KagyurAudio,Yana,Sermon,TranslationType
from schemas import (
    MainCategoryWithSubCategories, 
    SubCategoryResponse, KagyurTextResponse,  AudioResponse,FilterOptionsResponse,PaginatedResponse,SearchSuggestionResponse,KarchagStatsResponse
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
    query = db.query(KagyurAudio).filter(
        KagyurAudio.text_id == text_id,
        KagyurAudio.is_active == True
    )
    
    # Apply quality filter if specified
    if quality:
        query = query.filter(KagyurAudio.audio_quality == quality)
    
    audio_files = query.order_by(KagyurAudio.order_index).all()
    
    return {"audio_files": [AudioResponse.model_validate(audio) for audio in audio_files]}

@router.get("/audio/{audio_id}", tags=["Audio"])
async def get_audio_details(
    audio_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific audio file details and streaming URL"""
    audio = db.query(KagyurAudio).filter(
        KagyurAudio.id == audio_id,
        KagyurAudio.is_active == True
    ).first()
    
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return AudioResponse.model_validate(audio)
@router.get("/search", response_model=PaginatedResponse)
async def search_texts(
    q: Optional[str] = Query(None, description="Search term to look for in title and content"),
    category_id: Optional[int] = Query(None, description="Filter by main category ID"),
    sub_category_id: Optional[int] = Query(None, description="Filter by sub category ID"),
    sermon_id: Optional[int] = Query(None, description="Filter by sermon ID"),
    yana_id: Optional[int] = Query(None, description="Filter by yana ID"),
    translation_type_id: Optional[int] = Query(None, description="Filter by translation type ID"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    lang: Optional[str] = Query("en", regex="^(en|tb)$", description="Language: en for English, tb for Tibetan"),
    db: Session = Depends(get_db)
):
    """
    Search and filter texts with pagination support.
    
    - **q**: Search term to look for in title and content
    - **category_id**: Filter by main category
    - **sub_category_id**: Filter by sub category
    - **sermon_id**: Filter by specific sermon
    - **yana_id**: Filter by specific yana
    - **translation_type_id**: Filter by specific translation type
    - **page**: Page number (starts from 1)
    - **limit**: Items per page (1-100)
    - **lang**: Language preference (en/tb)
    """
    try:
        # Start building the query
        query = db.query(KagyurText).filter(KagyurText.is_active == True)
        
        # Apply filters
        filters = []
        
        # Text search in title fields
        if q and q.strip():
            search_term = f"%{q.strip()}%"
            if lang == "tb":
                # Search in Tibetan fields
                filters.append(
                    or_(
                        func.lower(KagyurText.tibetan_title).like(func.lower(search_term)),
                        func.lower(KagyurText.chinese_title).like(func.lower(search_term)),
                        func.lower(KagyurText.sanskrit_title).like(func.lower(search_term))
                    )
                )
            else:
                # Search in English fields
                filters.append(
                    func.lower(KagyurText.english_title).like(func.lower(search_term))
                )
        
        # Sub category filter (direct relationship)
        if sub_category_id:
            filters.append(KagyurText.sub_category_id == sub_category_id)
        
        # Main category filter (through sub_category relationship)
        if category_id:
            filters.append(SubCategory.main_category_id == category_id)
        
        # Sermon filter
        if sermon_id:
            filters.append(KagyurText.sermon_id == sermon_id)
        
        # Yana filter
        if yana_id:
            filters.append(KagyurText.yana_id == yana_id)
        
        # Translation type filter
        if translation_type_id:
            filters.append(KagyurText.translation_type_id == translation_type_id)
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Add joins for related data - only join SubCategory if we need main category filter
        if category_id:
            query = query.join(SubCategory, KagyurText.sub_category_id == SubCategory.id)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and eager load relationships
        offset = (page - 1) * limit
        texts = query.options(
            joinedload(KagyurText.sub_category).joinedload(SubCategory.main_category),
            joinedload(KagyurText.sermon),
            joinedload(KagyurText.yana),
            joinedload(KagyurText.translation_type),
            joinedload(KagyurText.text_summary),
            joinedload(KagyurText.yeshe_de_spans).joinedload(YesheDESpan.volumes)
        ).offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        # Convert to dict format for PaginatedResponse
        text_items = []
        for text in texts:
            text_dict = {
                "id": text.id,
                "derge_id": text.derge_id,
                "yeshe_de_id": text.yeshe_de_id,
                "tibetan_title": text.tibetan_title,
                "chinese_title": text.chinese_title,
                "sanskrit_title": text.sanskrit_title,
                "english_title": text.english_title,
                "sub_category_id": text.sub_category_id,
                "sermon_id": text.sermon_id,
                "yana_id": text.yana_id,
                "translation_type_id": text.translation_type_id,
                "order_index": text.order_index,
                "is_active": text.is_active,
                "created_at": text.created_at.isoformat() if text.created_at else None,
                "updated_at": text.updated_at.isoformat() if text.updated_at else None,
                # Related objects
                "sub_category": {
                    "id": text.sub_category.id,
                    "name_english": text.sub_category.name_english,
                    "name_tibetan": text.sub_category.name_tibetan,
                    "main_category": {
                        "id": text.sub_category.main_category.id,
                        "name_english": text.sub_category.main_category.name_english,
                        "name_tibetan": text.sub_category.main_category.name_tibetan
                    } if text.sub_category.main_category else None
                } if text.sub_category else None,
                "sermon": {
                    "id": text.sermon.id,
                    "name_english": text.sermon.name_english,
                    "name_tibetan": text.sermon.name_tibetan
                } if text.sermon else None,
                "yana": {
                    "id": text.yana.id,
                    "name_english": text.yana.name_english,
                    "name_tibetan": text.yana.name_tibetan
                } if text.yana else None,
                "translation_type": {
                    "id": text.translation_type.id,
                    "name_english": text.translation_type.name_english,
                    "name_tibetan": text.translation_type.name_tibetan
                } if text.translation_type else None,
                "text_summary": {
                    "id": text.text_summary.id,
                    "translator_homage_english": text.text_summary.translator_homage_english,
                    "translator_homage_tibetan": text.text_summary.translator_homage_tibetan,
                    "purpose_english": text.text_summary.purpose_english,
                    "purpose_tibetan": text.text_summary.purpose_tibetan,
                    "text_summary_english": text.text_summary.text_summary_english,
                    "text_summary_tibetan": text.text_summary.text_summary_tibetan
                } if text.text_summary else None,
                "yeshe_de_spans": [
                    {
                        "id": span.id,
                        "volumes": [
                            {
                                "id": vol.id,
                                "volume_number": vol.volume_number,
                                "start_page": vol.start_page,
                                "end_page": vol.end_page,
                                "order_index": vol.order_index
                            } for vol in span.volumes
                        ]
                    } for span in text.yeshe_de_spans
                ]
            }
            text_items.append(text_dict)
        
        logger.info(f"Search query: '{q}', filters: main_category={category_id}, sub_category={sub_category_id}, "
                   f"sermon={sermon_id}, yana={yana_id}, translation_type={translation_type_id}, "
                   f"page={page}, limit={limit}, lang={lang}, results={len(texts)}")
        
        return PaginatedResponse(
            items=text_items,
            total=total_count,
            page=page,
            limit=limit,
            pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error in search_texts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_filter_options(
    lang: Optional[str] = Query("en", regex="^(en|tb)$", description="Language: en for English, tb for Tibetan"),
    db: Session = Depends(get_db)
):
    """
    Get all available filter options for the search functionality.
    
    Returns categories, sermons, yanas, and translation types that can be used as filters.
    
    - **lang**: Language preference (en/tb) - affects which language version of names to return
    """
    try:
        # Get all main categories
        categories = db.query(MainCategory).filter(MainCategory.is_active == True).all()
        
        # Get all sermons
        sermons = db.query(Sermon).filter(Sermon.is_active == True).all()
        
        # Get all yanas
        yanas = db.query(Yana).filter(Yana.is_active == True).all()
        
        # Get all translation types
        translation_types = db.query(TranslationType).filter(TranslationType.is_active == True).all()
        
        logger.info(f"Retrieved filter options: {len(categories)} categories, "
                   f"{len(sermons)} sermons, {len(yanas)} yanas, "
                   f"{len(translation_types)} translation types")
        
        return FilterOptionsResponse(
            categories=categories,
            sermons=sermons,
            yanas=yanas,
            translation_types=translation_types,
            language=lang
        )
        
    except Exception as e:
        logger.error(f"Error in get_filter_options: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Search term for suggestions"),
    lang: Optional[str] = Query("en", regex="^(en|tb)$", description="Language preference"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial input.
    
    This endpoint returns text titles that match the partial search term
    to help users with autocomplete functionality.
    """
    try:
        search_term = f"%{q.strip()}%"
        
        if lang == "tb":
            # Search in Tibetan and other non-English titles
            suggestions = db.query(KagyurText.tibetan_title)\
                           .filter(
                               and_(
                                   KagyurText.is_active == True,
                                   func.lower(KagyurText.tibetan_title).like(func.lower(search_term))
                               )
                           )\
                           .distinct()\
                           .limit(limit)\
                           .all()
            suggestion_list = [suggestion[0] for suggestion in suggestions if suggestion[0]]
        else:
            # Search in English titles
            suggestions = db.query(KagyurText.english_title)\
                           .filter(
                               and_(
                                   KagyurText.is_active == True,
                                   func.lower(KagyurText.english_title).like(func.lower(search_term))
                               )
                           )\
                           .distinct()\
                           .limit(limit)\
                           .all()
            suggestion_list = [suggestion[0] for suggestion in suggestions if suggestion[0]]
        
        return SearchSuggestionResponse(
            suggestions=suggestion_list,
            query=q,
            language=lang
        )
            
    except Exception as e:
        logger.error(f"Error in get_search_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats", response_model=KarchagStatsResponse)
async def get_karchag_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about the karchag collection.
    
    Returns counts of texts, categories, sermons, etc.
    """
    try:
        # Get texts by main category
        texts_by_category = db.query(MainCategory.name_english, func.count(KagyurText.id))\
                             .join(SubCategory, MainCategory.id == SubCategory.main_category_id)\
                             .join(KagyurText, SubCategory.id == KagyurText.sub_category_id)\
                             .filter(KagyurText.is_active == True)\
                             .group_by(MainCategory.id, MainCategory.name_english)\
                             .all()
        
        # Get texts by yana
        texts_by_yana = db.query(Yana.name_english, func.count(KagyurText.id))\
                          .join(KagyurText, Yana.id == KagyurText.yana_id)\
                          .filter(KagyurText.is_active == True)\
                          .group_by(Yana.id, Yana.name_english)\
                          .all()
        
        stats = KarchagStatsResponse(
            total_texts=db.query(KagyurText).filter(KagyurText.is_active == True).count(),
            total_categories=db.query(MainCategory).filter(MainCategory.is_active == True).count(),
            total_sermons=db.query(Sermon).filter(Sermon.is_active == True).count(),
            total_yanas=db.query(Yana).filter(Yana.is_active == True).count(),
            total_translation_types=db.query(TranslationType).filter(TranslationType.is_active == True).count(),
            texts_by_category=texts_by_category,
            texts_by_yana=texts_by_yana
        )
        
        logger.info("Retrieved karchag statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_karchag_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Additional endpoint to get sub-categories by main category
@router.get("/categories/{category_id}/sub-categories")
async def get_sub_categories(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all sub-categories for a specific main category.
    
    Useful for cascading dropdowns in the UI.
    """
    try:
        sub_categories = db.query(SubCategory)\
                          .filter(
                              and_(
                                  SubCategory.main_category_id == category_id,
                                  SubCategory.is_active == True
                              )
                          )\
                          .order_by(SubCategory.order_index, SubCategory.name_english)\
                          .all()
        
        return [
            {
                "id": sub_cat.id,
                "name_english": sub_cat.name_english,
                "name_tibetan": sub_cat.name_tibetan,
                "description_english": sub_cat.description_english,
                "description_tibetan": sub_cat.description_tibetan,
                "order_index": sub_cat.order_index
            }
            for sub_cat in sub_categories
        ]
        
    except Exception as e:
        logger.error(f"Error in get_sub_categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")