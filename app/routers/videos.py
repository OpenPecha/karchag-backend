from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import  User
from app.schemas import VideoResponse, VideoCreate, VideoUpdate, VideoPublish, VideoPublishResponse
from app.dependencies.auth import require_admin
from app.services.video_service.handleGetVideos import handle_get_videos
from app.services.video_service.handleGetVideoDetail import handle_get_video_detail
from app.services.video_service.handleGetLatestVideos import handle_get_latest_videos
from app.services.video_service.handleGetAllVideosAdmin import handle_get_all_videos_admin
from app.services.video_service.handleGetVideoDetailAdmin import handle_get_video_detail_admin
from app.services.video_service.handleCreateVideo import handle_create_video
from app.services.video_service.handleUpdateVideo import handle_update_video
from app.services.video_service.handleDeleteVideo import handle_delete_video
from app.services.video_service.handlePublishVideo import handle_publish_video
from app.services.video_service.handleUnpublishVideo import handle_unpublish_video

router = APIRouter(tags=["videos"])

# ==================== SPECIFIC ROUTES (must come before parameterized routes) ====================

@router.get("/videos/latest", response_model=List[VideoResponse])
async def get_latest_videos(
    limit: int = Query(5, ge=1, le=20),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """🌍 Get latest published videos"""
    return await handle_get_latest_videos(limit=limit, lang=lang, db=db)

@router.get("/videos/all", tags=["Video Management"])
async def get_all_videos_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """🔒 Get all videos (including inactive) - Admin only"""
    return await handle_get_all_videos_admin(page=page, limit=limit, search=search, current_user=current_user, db=db)

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/videos")
async def get_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """🌍 Get published videos with pagination"""
    return await handle_get_videos(page=page, limit=limit, lang=lang, db=db)

@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video_detail(
    video_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """🌍 Get published video details"""
    return await handle_get_video_detail(video_id=video_id, lang=lang, db=db)

# ==================== ADMIN ENDPOINTS ====================

@router.post("/videos", response_model=VideoResponse, status_code=status.HTTP_201_CREATED, tags=["Video Management"])
async def create_video(
    video_data: VideoCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """🔒 Create new video - Admin only"""
    return await handle_create_video(video_data=video_data, current_user=current_user, db=db)

@router.get("/videos/{video_id}/details", tags=["Video Management"])
async def get_video_detail_admin(
    video_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """🔒 Get video details for editing - Admin only"""
    return await handle_get_video_detail_admin(video_id=video_id, current_user=current_user, db=db)

@router.put("/videos/{video_id}", response_model=VideoResponse, tags=["Video Management"])
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """🔒 Update video - Admin only"""
    return await handle_update_video(video_id=video_id, video_data=video_data, current_user=current_user, db=db)

@router.delete("/videos/{video_id}", tags=["Video Management"])
async def delete_video(
    video_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """🔒 Delete video - Admin only"""
    return await handle_delete_video(video_id=video_id, current_user=current_user, db=db)

# ==================== PUBLISH/UNPUBLISH ENDPOINTS ====================

@router.patch("/videos/{video_id}/publish", response_model=VideoPublishResponse, tags=["Video Management"])
async def publish_video(
    video_id: int,
    publish_data: VideoPublish,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """🔒 Publish a video"""
    video = await handle_publish_video(db, video_id, current_user.id, publish_data.published_date)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoPublishResponse(
        success=True,
        message="Video published successfully",
        data=VideoResponse.from_orm(video)
    )

@router.patch("/videos/{video_id}/unpublish", response_model=VideoPublishResponse, tags=["Video Management"])
async def unpublish_video(
    video_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """🔒 Unpublish a video"""
    video = await handle_unpublish_video(db, video_id, current_user.id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoPublishResponse(
        success=True,
        message="Video unpublished successfully",
        data=VideoResponse.from_orm(video)
    )
