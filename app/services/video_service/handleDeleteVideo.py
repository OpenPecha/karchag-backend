from sqlalchemy.orm import Session
from models import KagyurVideo, User
from fastapi import HTTPException

async def handle_delete_video(video_id: int, current_user: User, db: Session) -> dict:
    video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(video)
    db.commit()
    return {"message": "Video deleted successfully"} 