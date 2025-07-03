from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from models import  User
from schemas import VideoResponse, VideoCreate, VideoUpdate
from app.dependencies.auth import require_admin
from app.services.video_service.handleGetVideos import handle_get_videos
from app.services.video_service.handleGetVideoDetail import handle_get_video_detail
from app.services.video_service.handleGetLatestVideos import handle_get_latest_videos
from app.services.video_service.handleGetAllVideosAdmin import handle_get_all_videos_admin
from app.services.video_service.handleGetVideoDetailAdmin import handle_get_video_detail_admin
from app.services.video_service.handleCreateVideo import handle_create_video
from app.services.video_service.handleUpdateVideo import handle_update_video
from app.services.video_service.handleDeleteVideo import handle_delete_video

router = APIRouter(tags=["videos"])

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/videos")
async def get_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active videos with pagination"""
    return await handle_get_videos(page=page, limit=limit, lang=lang, db=db)

@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video_detail(
    video_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific video detail"""
    return await handle_get_video_detail(video_id=video_id, lang=lang, db=db)

@router.get("/videos/latest", response_model=List[VideoResponse])
async def get_latest_videos(
    limit: int = Query(5, ge=1, le=20),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get latest videos"""
    return await handle_get_latest_videos(limit=limit, lang=lang, db=db)

# ==================== ADMIN ENDPOINTS ====================

@router.get("/videos/all", tags=["Video Management"])
async def get_all_videos_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all videos (including inactive) - Admin only"""
    return await handle_get_all_videos_admin(page=page, limit=limit, search=search, current_user=current_user, db=db)

@router.get("/videos/{video_id}/details", tags=["Video Management"])
async def get_video_detail_admin(
    video_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific video detail for editing - Admin only"""
    return await handle_get_video_detail_admin(video_id=video_id, current_user=current_user, db=db)

@router.post("/videos", response_model=VideoResponse, status_code=status.HTTP_201_CREATED, tags=["Video Management"])
async def create_video(
    video_data: VideoCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new video - Admin only"""
    return await handle_create_video(video_data=video_data, current_user=current_user, db=db)

@router.put("/videos/{video_id}", response_model=VideoResponse, tags=["Video Management"])
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update video - Admin only"""
    return await handle_update_video(video_id=video_id, video_data=video_data, current_user=current_user, db=db)

@router.delete("/videos/{video_id}", tags=["Video Management"])
async def delete_video(
    video_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete video - Admin only"""
    return await handle_delete_video(video_id=video_id, current_user=current_user, db=db)
