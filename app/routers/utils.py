from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func,and_, or_
from typing import List, Optional
from app.database import get_db
from app.models import MainCategory, SubCategory, KagyurText, TextSummary, YesheDESpan, Volume, KagyurAudio,Yana,Sermon,TranslationType
from app.schemas import (MainCategoryResponse, MainCategoryCreate, SubCategoryUpdate,
    MainCategoryWithSubCategories,SubCategoryResponse,SubCategoryCreateRequest,   AudioResponse,FilterOptionsResponse,PaginatedResponse,SearchSuggestionResponse,KarchagStatsResponse
)
import logging

router = APIRouter(prefix="/categories", tags=["Utils"])
logger = logging.getLogger(__name__)


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

