from sqlalchemy.orm import Session
from app.models import KagyurVideo, User
from typing import Optional

async def handle_get_all_videos_admin(page: int, limit: int, search: Optional[str], current_user: User, db: Session) -> dict:
    query = db.query(KagyurVideo)
    if search:
        query = query.filter(
            KagyurVideo.english_title.ilike(f"%{search}%") |
            KagyurVideo.tibetan_title.ilike(f"%{search}%")
        )
    total = query.count()
    videos = query.order_by(KagyurVideo.published_date.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "videos": videos,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    } 