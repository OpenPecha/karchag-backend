from sqlalchemy.orm import Session
from app.models import KagyurVideo
from typing import Optional

async def handle_get_videos(page: int, limit: int, lang: Optional[str], db: Session) -> dict:
    offset = (page - 1) * limit
    query = db.query(KagyurVideo).filter(KagyurVideo.is_active == True)
    total = query.count()
    videos = query.order_by(KagyurVideo.published_date.desc()).offset(offset).limit(limit).all()
    return {
        "videos": videos,
        "pagination": {
            "current_page": page,
            "per_page": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    } 