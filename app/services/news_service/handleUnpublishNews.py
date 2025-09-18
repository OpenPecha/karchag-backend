from sqlalchemy.orm import Session
from app.models import KagyurNews, User, PublicationStatus
from app.schemas import NewsUnpublish
from fastapi import HTTPException
from datetime import datetime
from typing import Any

async def handle_unpublish_news(news_id: int, unpublish_data: NewsUnpublish, current_user: User, db: Session) -> Any:
    """Unpublish a news article"""
    news = db.query(KagyurNews).filter(KagyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Update publication status
    setattr(news, 'publication_status', PublicationStatus.UNPUBLISHED)
    setattr(news, 'is_active', False)
    setattr(news, 'updated_at', datetime.now())
    
    db.commit()
    db.refresh(news)
    return news 