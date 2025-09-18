from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import KagyurVideo
from app.utils.audit import log_activity

async def handle_unpublish_video(db: Session, video_id: int, user_id: int):
    """
    Unpublish a video by setting its publication status to 'unpublished'
    """
    try:
        # Get the video
        video = db.query(KagyurVideo).filter(KagyurVideo.id == video_id).first()
        if not video:
            return None
        
        old_status = video.publication_status
        
        # Set unpublished status
        video.publication_status = "unpublished"
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
            action="UNPUBLISH",
            old_values={"publication_status": old_status},
            new_values={"publication_status": "unpublished"}
        )
        
        return video
        
    except Exception as e:
        db.rollback()
        raise e
