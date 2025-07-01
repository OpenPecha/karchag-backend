from sqlalchemy.orm import Session
from models import KagyurNews, User
from typing import Optional

async def handle_get_all_news_admin(page: int, limit: int, search: Optional[str], current_user: User, db: Session) -> dict:
    query = db.query(KagyurNews)
    if search:
        query = query.filter(
            KagyurNews.english_title.ilike(f"%{search}%") |
            KagyurNews.tibetan_title.ilike(f"%{search}%")
        )
    total = query.count()
    news_list = query.order_by(KagyurNews.published_date.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "news": news_list,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    } 