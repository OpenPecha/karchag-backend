from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models import KagyurVideo
from app.utils.audit import log_activity

async def handle_publish_video(db: Session, video_id: int, user_id: int, published_date: datetime = None):
    """
    Publish a video by setting its publication status to 'published'
    """
    try:
        # Get the video
        video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
        if not video:
            return None
        
        old_status = video.publication_status
        
        # Set publication details
        video.publication_status = "published"
        video.published_date = published_date or datetime.utcnow()
        video.updated_at = func.now()
        
        # Commit changes
        db.commit()
        db.refresh(video)
        
        # Log audit
        log_activity(
            db=db,
            user_id=user_id,
            table_name="kangyur_video",
            record_id=video.id,
            action="PUBLISH",
            old_values={"publication_status": old_status},
            new_values={"publication_status": "published", "published_date": str(video.published_date)}
        )
        
        return video
        
    except Exception as e:
        db.rollback()
        raise e
