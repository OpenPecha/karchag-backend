from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import KagyurVideo
from schemas import VideoResponse, PaginatedResponse
import math

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all available video content"""
    offset = (page - 1) * limit
    
    query = db.query(KagyurVideo).filter(KagyurVideo.is_active == True)
    total = query.count()
    
    videos = query.order_by(KagyurVideo.published_date.desc()).offset(offset).limit(limit).all()
    
    return PaginatedResponse(
        items=[VideoResponse.from_orm(video).dict() for video in videos],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit)
    )

@router.get("/{video_id}")
async def get_video_details(
    video_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific video details and streaming URL"""
    video = db.query(KagyurVideo).filter(
        KagyurVideo.id == video_id,
        KagyurVideo.is_active == True
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoResponse.from_orm(video)

@router.get("/latest")
async def get_latest_videos(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get latest 5 published videos"""
    videos = db.query(KagyurVideo).filter(
        KagyurVideo.is_active == True
    ).order_by(KagyurVideo.published_date.desc()).limit(5).all()
    
    return {"videos": [VideoResponse.from_orm(video) for video in videos]}