from sqlalchemy.orm import Session
from app.models import KagyurNews
from app.schemas import NewsResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_news_detail(news_id: int, lang: Optional[str], db: Session) -> NewsResponse:
    news = db.query(KagyurNews).filter(
        KagyurNews.id == news_id,
        KagyurNews.is_active == True
    ).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news 