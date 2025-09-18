from sqlalchemy.orm import Session
from app.models import KagyurNews, User, PublicationStatus
from app.schemas import NewsUpdate
from fastapi import HTTPException
from datetime import datetime

async def handle_update_news(news_id: int, news_data: NewsUpdate, current_user: User, db: Session):
    news = db.query(KagyurNews).filter(KagyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    update_data = news_data.model_dump(exclude_unset=True)
    
    # Handle publication status changes
    if 'publication_status' in update_data:
        new_status = update_data['publication_status']
        if new_status == PublicationStatus.PUBLISHED and not update_data.get('published_date'):
            # If publishing without a date, use current time
            update_data['published_date'] = datetime.now()
        elif new_status != PublicationStatus.PUBLISHED:
            # If not publishing, clear the published date
            update_data['published_date'] = None
    
    for field, value in update_data.items():
        setattr(news, field, value)
    
    setattr(news, 'updated_at', datetime.now())
    db.commit()
    db.refresh(news)
    return news 