from sqlalchemy.orm import Session
from app.models import KagyurVideo
from app.schemas import VideoResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_video_detail(video_id: int, lang: Optional[str], db: Session) -> VideoResponse:
    # Only show published videos for public access
    video = db.query(KagyurVideo).filter(
        KagyurVideo.id == video_id,
        KagyurVideo.is_active == True,
        KagyurVideo.publication_status == "published"
    ).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video 