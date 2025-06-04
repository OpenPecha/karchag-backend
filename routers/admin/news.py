from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import KangyurNews
from schemas import NewsCreate, NewsUpdate, NewsPublish

router = APIRouter(
    tags=["News Management"]
)

@router.get("/news")
async def get_all_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query("all", regex="^(all|published|draft)$"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all news articles with filters"""
    query = db.query(KangyurNews)
    
    # Apply status filter
    if status == "published":
        query = query.filter(
            KangyurNews.is_active == True,
            KangyurNews.published_date.isnot(None)
        )
    elif status == "draft":
        query = query.filter(
            KangyurNews.published_date.is_(None)
        )
    
    # Apply search filter
    if search:
        query = query.filter(
            KangyurNews.english_title.ilike(f"%{search}%") |
            KangyurNews.tibetan_title.ilike(f"%{search}%") |
            KangyurNews.english_content.ilike(f"%{search}%") |
            KangyurNews.tibetan_content.ilike(f"%{search}%")
        )
    
    # Order by created_at descending (newest first)
    query = query.order_by(KangyurNews.created_at.desc())
    
    # Pagination
    total = query.count()
    news_articles = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "news_articles": news_articles,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/news/{news_id}")
async def get_news_details(
    news_id: int,
    db: Session = Depends(get_db)
):
    """Get specific news article for editing"""
    news = db.query(KangyurNews).filter(KangyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    return news

@router.post("/news")
async def create_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db)
):
    """Create new news article"""
    news = KangyurNews(
        tibetan_title=news_data.tibetan_title,
        english_title=news_data.english_title,
        tibetan_content=news_data.tibetan_content,
        english_content=news_data.english_content,
        published_date=news_data.published_date if hasattr(news_data, 'published_date') else None,
        is_active=news_data.is_active if hasattr(news_data, 'is_active') else True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(news)
    db.commit()
    db.refresh(news)
    
    return news

@router.put("/news/{news_id}")
async def update_news(
    news_id: int,
    news_update: NewsUpdate,
    db: Session = Depends(get_db)
):
    """Update news article"""
    news = db.query(KangyurNews).filter(KangyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Update fields
    for field, value in news_update.dict(exclude_unset=True).items():
        setattr(news, field, value)
    
    news.updated_at = datetime.now()
    db.commit()
    db.refresh(news)
    
    return news

@router.delete("/news/{news_id}")
async def delete_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    """Delete news article"""
    news = db.query(KangyurNews).filter(KangyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    db.delete(news)
    db.commit()
    
    return {"message": "News article deleted successfully"}

@router.post("/news/{news_id}/publish")
async def publish_news(
    news_id: int,
    publish_data: NewsPublish,
    db: Session = Depends(get_db)
):
    """Publish news article"""
    news = db.query(KangyurNews).filter(KangyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Set published date and activate
    news.published_date = publish_data.published_date
    news.is_active = True
    news.updated_at = datetime.now()
    
    db.commit()
    db.refresh(news)
    
    return news

@router.post("/news/{news_id}/unpublish")
async def unpublish_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    """Unpublish news article"""
    news = db.query(KangyurNews).filter(KangyurNews.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Remove published date to make it draft
    news.published_date = None
    news.updated_at = datetime.now()
    
    db.commit()
    db.refresh(news)
    
    return news

# Additional utility endpoints
@router.get("/news/stats")
async def get_news_stats(db: Session = Depends(get_db)):
    """Get news statistics"""
    total_news = db.query(KangyurNews).count()
    published_news = db.query(KangyurNews).filter(
        KangyurNews.is_active == True,
        KangyurNews.published_date.isnot(None)
    ).count()
    draft_news = db.query(KangyurNews).filter(
        KangyurNews.published_date.is_(None)
    ).count()
    
    return {
        "total_news": total_news,
        "published_news": published_news,
        "draft_news": draft_news,
        "inactive_news": total_news - published_news - draft_news
    }

@router.get("/news/recent")
async def get_recent_news(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get recent published news articles"""
    recent_news = db.query(KangyurNews).filter(
        KangyurNews.is_active == True,
        KangyurNews.published_date.isnot(None)
    ).order_by(KangyurNews.published_date.desc()).limit(limit).all()
    
    return {"recent_news": recent_news}