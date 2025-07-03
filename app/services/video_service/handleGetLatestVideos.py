from sqlalchemy.orm import Session
from models import KagyurVideo
from schemas import VideoResponse
from typing import Optional, List

async def handle_get_latest_videos(limit: int, lang: Optional[str], db: Session) -> list:
    videos = db.query(KagyurVideo).filter(
        KagyurVideo.is_active == True
    ).order_by(KagyurVideo.published_date.desc()).limit(limit).all()
    return videos 