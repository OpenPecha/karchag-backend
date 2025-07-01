from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from database import get_db
from models import KagyurNews, User
from schemas import NewsResponse, NewsCreate, NewsUpdate
from dependencies.auth import require_admin
import math
from datetime import datetime
from services.news_service.handleGetNews import handle_get_news
from services.news_service.handleGetNewsDetail import handle_get_news_detail
from services.news_service.handleGetLatestNews import handle_get_latest_news
from services.news_service.handleGetAllNewsAdmin import handle_get_all_news_admin
from services.news_service.handleGetNewsDetailAdmin import handle_get_news_detail_admin
from services.news_service.handleCreateNews import handle_create_news
from services.news_service.handleUpdateNews import handle_update_news
from services.news_service.handleDeleteNews import handle_delete_news

router = APIRouter(tags=["news"])


@router.get("/news")
async def get_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active news with pagination"""
    return await handle_get_news(page=page, limit=limit, lang=lang, db=db)

@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news_detail(
    news_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific news detail"""
    return await handle_get_news_detail(news_id=news_id, lang=lang, db=db)

@router.get("/news/latest", response_model=List[NewsResponse])
async def get_latest_news(
    limit: int = Query(5, ge=1, le=20),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get latest news articles"""
    return await handle_get_latest_news(limit=limit, lang=lang, db=db)

@router.get("/news/all", tags=["News Management"])
async def get_all_news_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all news (including inactive) - Admin only"""
    return await handle_get_all_news_admin(page=page, limit=limit, search=search, current_user=current_user, db=db)

@router.get("/news/{news_id}/details", tags=["News Management"])
async def get_news_detail_admin(
    news_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific news detail for editing - Admin only"""
    return await handle_get_news_detail_admin(news_id=news_id, current_user=current_user, db=db)

@router.post("/news", response_model=NewsResponse, status_code=status.HTTP_201_CREATED, tags=["News Management"])
async def create_news(
    news_data: NewsCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new news article - Admin only"""
    return await handle_create_news(news_data=news_data, current_user=current_user, db=db)

@router.put("/news/{news_id}", response_model=NewsResponse, tags=["News Management"])
async def update_news(
    news_id: int,
    news_data: NewsUpdate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update news article - Admin only"""
    return await handle_update_news(news_id=news_id, news_data=news_data, current_user=current_user, db=db)

@router.delete("/news/{news_id}", tags=["News Management"])
async def delete_news(
    news_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete news article - Admin only"""
    return await handle_delete_news(news_id=news_id, current_user=current_user, db=db)
