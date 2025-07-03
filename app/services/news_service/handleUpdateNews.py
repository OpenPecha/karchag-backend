from sqlalchemy.orm import Session
from app.models import KagyurNews, User
from app.schemas import NewsUpdate
from fastapi import HTTPException
from datetime import datetime

async def handle_update_news(news_id: int, news_data: NewsUpdate, current_user: User, db: Session):
    news = db.query(KagyurNews).filter(KagyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    update_data = news_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(news, field, value)
    news.updated_at = datetime.now()
    db.commit()
    db.refresh(news)
    return news 