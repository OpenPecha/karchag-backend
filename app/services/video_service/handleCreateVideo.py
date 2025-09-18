from sqlalchemy.orm import Session
from app.models import KagyurVideo, User
from app.schemas import VideoCreate
from datetime import datetime

async def handle_create_video(video_data: VideoCreate, current_user: User, db: Session):
    video = KagyurVideo(
        tibetan_title=video_data.tibetan_title,
        english_title=video_data.english_title,
        tibetan_description=video_data.tibetan_description,
        english_description=video_data.english_description,
        video_url=video_data.video_url,
        published_date=video_data.published_date or datetime.now(),
        is_active=video_data.is_active
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video 