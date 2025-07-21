from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .base import TimestampMixin, PaginatedResponse


class PublicationStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"


class NewsBase(BaseModel):
    tibetan_title: str
    english_title: str
    tibetan_content: str
    english_content: str


class NewsCreate(NewsBase):
    published_date: Optional[datetime] = None
    publication_status: Optional[PublicationStatus] = PublicationStatus.DRAFT
    is_active: Optional[bool] = True


class NewsUpdate(BaseModel):
    tibetan_title: Optional[str] = None
    english_title: Optional[str] = None
    tibetan_content: Optional[str] = None
    english_content: Optional[str] = None
    published_date: Optional[datetime] = None
    publication_status: Optional[PublicationStatus] = None
    is_active: Optional[bool] = None


class NewsPublish(BaseModel):
    published_date: datetime


class NewsUnpublish(BaseModel):
    pass


class NewsResponse(NewsBase, TimestampMixin):
    id: int
    published_date: Optional[datetime] = None
    publication_status: PublicationStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class NewsPaginatedResponse(PaginatedResponse):
    news_articles: List[NewsResponse]