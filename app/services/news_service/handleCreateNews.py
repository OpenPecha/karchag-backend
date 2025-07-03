from sqlalchemy.orm import Session
from app.models import KagyurNews, User
from app.schemas import NewsCreate
from datetime import datetime

async def handle_create_news(news_data: NewsCreate, current_user: User, db: Session):
    now = datetime.now()
    news = KagyurNews(
        tibetan_title=news_data.tibetan_title,
        english_title=news_data.english_title,
        tibetan_content=news_data.tibetan_content,
        english_content=news_data.english_content,
        published_date=news_data.published_date or now,
        is_active=news_data.is_active,
        # Remove these lines - let SQLAlchemy handle timestamps automatically
        # created_at=now,
        # updated_at=now
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news