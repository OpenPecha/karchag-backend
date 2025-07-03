from sqlalchemy.orm import Session
from app.models import KagyurNews
from app.schemas import NewsResponse
from typing import Optional, List

async def handle_get_latest_news(limit: int, lang: Optional[str], db: Session) -> list:
    news_list = db.query(KagyurNews).filter(
        KagyurNews.is_active == True
    ).order_by(KagyurNews.published_date.desc()).limit(limit).all()
    return news_list 