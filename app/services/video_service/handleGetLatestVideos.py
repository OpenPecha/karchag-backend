from sqlalchemy.orm import Session
from app.models import KagyurVideo
from app.schemas import VideoResponse
from typing import Optional, List

async def handle_get_latest_videos(limit: int, lang: Optional[str], db: Session) -> list:
    # Only show published videos for public access
    videos = db.query(KagyurVideo).filter(
        KagyurVideo.is_active == True,
        KagyurVideo.publication_status == "published"
    ).order_by(KagyurVideo.published_date.desc()).limit(limit).all()
    return videos 