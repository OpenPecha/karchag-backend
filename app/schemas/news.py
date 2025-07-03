from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .base import TimestampMixin, PaginatedResponse


class NewsBase(BaseModel):
    tibetan_title: str
    english_title: str
    tibetan_content: str
    english_content: str


class NewsCreate(NewsBase):
    published_date: Optional[datetime] = None
    is_active: Optional[bool] = True


class NewsUpdate(BaseModel):
    tibetan_title: Optional[str] = None
    english_title: Optional[str] = None
    tibetan_content: Optional[str] = None
    english_content: Optional[str] = None
    published_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    created_at: datetime
    updated_at: datetime


class NewsPublish(BaseModel):
    published_date: datetime


class NewsResponse(NewsBase, TimestampMixin):
    id: int
    published_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NewsPaginatedResponse(PaginatedResponse):
    news_articles: List[NewsResponse]