from sqlalchemy.orm import Session
from app.models import KagyurVideo, User
from app.schemas import VideoUpdate
from fastapi import HTTPException

async def handle_update_video(video_id: int, video_data: VideoUpdate, current_user: User, db: Session):
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    update_data = video_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)
    db.commit()
    db.refresh(video)
    return video 