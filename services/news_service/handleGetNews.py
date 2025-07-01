from sqlalchemy.orm import Session
from models import KagyurNews
from typing import Optional

async def handle_get_news(page: int, limit: int, lang: Optional[str], db: Session) -> dict:
    offset = (page - 1) * limit
    query = db.query(KagyurNews).filter(KagyurNews.is_active == True)
    total = query.count()
    news_list = query.order_by(KagyurNews.published_date.desc()).offset(offset).limit(limit).all()
    return {
        "news": news_list,
        "pagination": {
            "current_page": page,
            "per_page": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    } 