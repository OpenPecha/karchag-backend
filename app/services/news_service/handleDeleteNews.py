from sqlalchemy.orm import Session
from app.models import KagyurNews, User
from fastapi import HTTPException

async def handle_delete_news(news_id: int, current_user: User, db: Session) -> dict:
    news = db.query(KagyurNews).filter(KagyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(news)
    db.commit()
    return {"message": "News deleted successfully"} 