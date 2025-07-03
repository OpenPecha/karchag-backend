from sqlalchemy.orm import Session
from app.models import KagyurVideo
from app.schemas import VideoResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_video_detail(video_id: int, lang: Optional[str], db: Session) -> VideoResponse:
    video = db.query(KagyurVideo).filter(
        KagyurVideo.id == video_id,
        KagyurVideo.is_active == True
    ).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video 