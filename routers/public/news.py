from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import KangyurNews
from schemas import NewsResponse, PaginatedResponse
import math

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_news(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get published news articles with pagination"""
    offset = (page - 1) * limit
    
    query = db.query(KangyurNews).filter(KangyurNews.is_active == True)
    total = query.count()
    
    news_items = query.order_by(KangyurNews.published_date.desc()).offset(offset).limit(limit).all()
    
    return PaginatedResponse(
        items=[NewsResponse.from_orm(item).dict() for item in news_items],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit)
    )

@router.get("/{news_id}")
async def get_news_details(
    news_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific news article details"""
    news = db.query(KangyurNews).filter(
        KangyurNews.id == news_id,
        KangyurNews.is_active == True
    ).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    return NewsResponse.from_orm(news)

@router.get("/latest")
async def get_latest_news(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get latest 5 published news articles"""
    news_items = db.query(KangyurNews).filter(
        KangyurNews.is_active == True
    ).order_by(KangyurNews.published_date.desc()).limit(5).all()
    
    return {"news": [NewsResponse.from_orm(item) for item in news_items]}