from sqlalchemy.orm import Session
from app.models import KagyurNews, User, PublicationStatus
from app.schemas import NewsPublish
from fastapi import HTTPException
from datetime import datetime
from typing import Any

async def handle_publish_news(news_id: int, publish_data: NewsPublish, current_user: User, db: Session) -> Any:
    """Publish a news article"""
    news = db.query(KagyurNews).filter(KagyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Update publication status and date
    setattr(news, 'publication_status', PublicationStatus.PUBLISHED)
    setattr(news, 'published_date', publish_data.published_date)
    setattr(news, 'is_active', True)
    setattr(news, 'updated_at', datetime.now())
    
    db.commit()
    db.refresh(news)
    return news 