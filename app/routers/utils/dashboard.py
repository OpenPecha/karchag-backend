from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from app.database import get_db
from app.models import MainCategory, SubCategory, KagyurText, Yana, Sermon, TranslationType, AuditLog, User
from app.schemas import KarchagStatsResponse
from app.dependencies.auth import require_admin
import logging

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)

@router.get("/stats", response_model=KarchagStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics for admin dashboard.
    
    Returns comprehensive stats about the collection.
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
        
        logger.info(f"Admin {current_user.username} retrieved dashboard statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard stats error: {str(e)}")


@router.get("/activity")
async def get_dashboard_activity(
    current_user: User = Depends(require_admin),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent activity for admin dashboard.
    
    Returns recent user activities and system events.
    """
    try:
        # Get recent audit logs
        recent_activities = db.query(AuditLog)\
                             .order_by(AuditLog.timestamp.desc())\
                             .limit(limit)\
                             .all()
        
        activities = []
        for activity in recent_activities:
            activities.append({
                "id": activity.id,
                "user_id": activity.user_id,
                "table_name": activity.table_name,
                "record_id": activity.record_id,
                "action": activity.action,
                "timestamp": activity.timestamp,
                "ip_address": activity.ip_address
            })
        
        logger.info(f"Admin {current_user.username} retrieved dashboard activity")
        return {
            "activities": activities,
            "total": len(activities),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard activity error: {str(e)}")
