from sqlalchemy.orm import Session
from app.models import KagyurVideo, User
from fastapi import HTTPException

async def handle_get_video_detail_admin(video_id: int, current_user: User, db: Session):
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video 