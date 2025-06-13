from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import KagyurVideo
from schemas import VideoCreate, VideoUpdate, VideoPublish

router = APIRouter(
    tags=["Video Management"]
)

@router.get("/video")
async def get_all_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: str = Query("all", regex="^(all|published|draft)$"),
    db: Session = Depends(get_db)
):
    """Get all video files"""
    query = db.query(KagyurVideo)
    
    # Apply status filter
    if status == "published":
        query = query.filter(
            KagyurVideo.is_active == True,
            KagyurVideo.published_date.isnot(None)
        )
    elif status == "draft":
        query = query.filter(
            KagyurVideo.published_date.is_(None)
        )
    
    # Apply search filter
    if search:
        query = query.filter(
            KagyurVideo.english_title.ilike(f"%{search}%") |
            KagyurVideo.tibetan_title.ilike(f"%{search}%") |
            KagyurVideo.english_description.ilike(f"%{search}%") |
            KagyurVideo.tibetan_description.ilike(f"%{search}%")
        )
    
    # Order by created_at descending (newest first)
    query = query.order_by(KagyurVideo.created_at.desc())
    
    # Pagination
    total = query.count()
    videos = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "videos": videos,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/video/{video_id}")
async def get_video_details(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Get specific video details for editing"""
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video

@router.post("/video")
async def create_video(
    video_data: VideoCreate,
    db: Session = Depends(get_db)
):
    """Create new video record"""
    # Validate video URL format
    if not video_data.video_url or not (
        video_data.video_url.startswith('http://') or 
        video_data.video_url.startswith('https://')
    ):
        raise HTTPException(status_code=400, detail="Invalid video URL format")
    
    video = KagyurVideo(
        tibetan_title=video_data.tibetan_title,
        english_title=video_data.english_title,
        tibetan_description=video_data.tibetan_description,
        english_description=video_data.english_description,
        video_url=video_data.video_url,
        published_date=video_data.published_date if hasattr(video_data, 'published_date') else None,
        is_active=video_data.is_active if hasattr(video_data, 'is_active') else True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return video

@router.put("/video/{video_id}")
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: Session = Depends(get_db)
):
    """Update video metadata"""
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Validate video URL if being updated
    if hasattr(video_update, 'video_url') and video_update.video_url:
        if not (video_update.video_url.startswith('http://') or 
                video_update.video_url.startswith('https://')):
            raise HTTPException(status_code=400, detail="Invalid video URL format")
    
    # Update fields
    for field, value in video_update.dict(exclude_unset=True).items():
        setattr(video, field, value)
    
    video.updated_at = datetime.now()
    db.commit()
    db.refresh(video)
    
    return video

@router.delete("/video/{video_id}")
async def delete_video(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Delete video record"""
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    db.delete(video)
    db.commit()
    
    return {"message": "Video deleted successfully"}

@router.post("/video/{video_id}/publish")
async def publish_video(
    video_id: int,
    publish_data: VideoPublish,
    db: Session = Depends(get_db)
):
    """Publish video"""
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Set published date and activate
    video.published_date = publish_data.published_date
    video.is_active = True
    video.updated_at = datetime.now()
    
    db.commit()
    db.refresh(video)
    
    return video

@router.post("/video/{video_id}/unpublish")
async def unpublish_video(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Unpublish video"""
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Remove published date to make it draft
    video.published_date = None
    video.updated_at = datetime.now()
    
    db.commit()
    db.refresh(video)
    
    return video

# Additional utility endpoints
@router.get("/video/stats")
async def get_video_stats(db: Session = Depends(get_db)):
    """Get video statistics"""
    total_videos = db.query(KagyurVideo).count()
    published_videos = db.query(KagyurVideo).filter(
        KagyurVideo.is_active == True,
        KagyurVideo.published_date.isnot(None)
    ).count()
    draft_videos = db.query(KagyurVideo).filter(
        KagyurVideo.published_date.is_(None)
    ).count()
    
    return {
        "total_videos": total_videos,
        "published_videos": published_videos,
        "draft_videos": draft_videos,
        "inactive_videos": total_videos - published_videos - draft_videos
    }

@router.get("/video/recent")
async def get_recent_videos(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get recent published videos"""
    recent_videos = db.query(KagyurVideo).filter(
        KagyurVideo.is_active == True,
        KagyurVideo.published_date.isnot(None)
    ).order_by(KagyurVideo.published_date.desc()).limit(limit).all()
    
    return {"recent_videos": recent_videos}

@router.get("/video/search")
async def search_videos(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search published videos"""
    videos = db.query(KagyurVideo).filter(
        KagyurVideo.is_active == True,
        KagyurVideo.published_date.isnot(None),
        (KagyurVideo.english_title.ilike(f"%{q}%") |
         KagyurVideo.tibetan_title.ilike(f"%{q}%") |
         KagyurVideo.english_description.ilike(f"%{q}%") |
         KagyurVideo.tibetan_description.ilike(f"%{q}%"))
    ).order_by(KagyurVideo.published_date.desc()).limit(limit).all()
    
    return {"videos": videos, "query": q}