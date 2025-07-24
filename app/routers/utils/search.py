from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import MainCategory, SubCategory, KagyurText, Yana, Sermon, TranslationType
from app.schemas import SearchSuggestionResponse, FilterOptionsResponse, MainCategoryBase, SermonBase, YanaBase, TranslationTypeBase
import logging

router = APIRouter(prefix="/search", tags=["Search"])
logger = logging.getLogger(__name__)

@router.get("", response_model=SearchSuggestionResponse)
async def search_suggestions(
    q: Optional[str] = Query(None, description="Search query"),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on query.
    
    Returns suggestions from text titles, categories, etc.
    """
    try:
        suggestions = []
        
        if q and len(q.strip()) >= 2:
            # Search in text titles
            text_suggestions = db.query(KagyurText.english_title if lang == "en" else KagyurText.tibetan_title)\
                                .filter(KagyurText.is_active == True)\
                                .filter(
                                    (KagyurText.english_title.ilike(f"%{q}%") if lang == "en" 
                                     else KagyurText.tibetan_title.ilike(f"%{q}%"))
                                )\
                                .limit(limit//2).all()
            
            # Search in categories
            category_suggestions = db.query(MainCategory.name_english if lang == "en" else MainCategory.name_tibetan)\
                                    .filter(MainCategory.is_active == True)\
                                    .filter(
                                        (MainCategory.name_english.ilike(f"%{q}%") if lang == "en" 
                                         else MainCategory.name_tibetan.ilike(f"%{q}%"))
                                    )\
                                    .limit(limit//2).all()
            
            # Flatten and clean suggestions
            for result in text_suggestions:
                if result[0] and result[0].strip():
                    suggestions.append(result[0].strip())
                    
            for result in category_suggestions:
                if result[0] and result[0].strip():
                    suggestions.append(result[0].strip())
            
            # Remove duplicates and limit
            suggestions = list(set(suggestions))[:limit]
        
        return SearchSuggestionResponse(
            suggestions=suggestions,
            query=q or "",
            language=lang
        )
        
    except Exception as e:
        logger.error(f"Error in search_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_filter_options(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """
    Get available filter options for search.
    
    Returns categories, sermons, yanas, and translation types.
    """
    try:
        # Get active categories
        categories = db.query(MainCategory)\
                      .filter(MainCategory.is_active == True)\
                      .order_by(MainCategory.order_index)\
                      .all()
        
        # Get active sermons
        sermons = db.query(Sermon)\
                   .filter(Sermon.is_active == True)\
                   .order_by(Sermon.order_index)\
                   .all()
        
        # Get active yanas
        yanas = db.query(Yana)\
                 .filter(Yana.is_active == True)\
                 .order_by(Yana.order_index)\
                 .all()
        
        # Get active translation types
        translation_types = db.query(TranslationType)\
                           .filter(TranslationType.is_active == True)\
                           .order_by(TranslationType.order_index)\
                           .all()
        
        return FilterOptionsResponse(
            categories=[MainCategoryBase(name_english=c.name_english, name_tibetan=c.name_tibetan) for c in categories],
            sermons=[SermonBase(name_english=s.name_english, name_tibetan=s.name_tibetan) for s in sermons],
            yanas=[YanaBase(name_english=y.name_english, name_tibetan=y.name_tibetan) for y in yanas],
            translation_types=[TranslationTypeBase(name_english=t.name_english, name_tibetan=t.name_tibetan) for t in translation_types],
            language=lang
        )
        
    except Exception as e:
        logger.error(f"Error in get_filter_options: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Filter options error: {str(e)}")
