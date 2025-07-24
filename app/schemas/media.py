from pydantic import BaseModel, validator
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from .base import TimestampMixin, PaginatedResponse
from .reference import PublicationStatus

if TYPE_CHECKING:
    from . import VideoResponse


class AudioBase(BaseModel):
    narrator_name_english: str
    narrator_name_tibetan: Optional[str] = ""
    audio_quality: Optional[str] = "standard"
    audio_language: Optional[str] = "tibetan"
    order_index: Optional[int] = 0
    is_active: Optional[bool] = True


class AudioCreate(AudioBase):
    pass


class AudioUpdate(BaseModel):
    narrator_name_english: Optional[str] = None
    narrator_name_tibetan: Optional[str] = None
    audio_quality: Optional[str] = None
    audio_language: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class AudioResponse(AudioBase, TimestampMixin):
    id: int
    text_id: int
    audio_url: str
    file_name: str
    file_size: int
    duration: Optional[int] = None
    
    class Config:
        from_attributes = True


class VideoBase(BaseModel):
    tibetan_title: str
    english_title: str
    tibetan_description: str
    english_description: str
    video_url: str
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Video URL must start with http:// or https://')
        return v


class VideoCreate(VideoBase):
    published_date: Optional[datetime] = None
    publication_status: Optional[PublicationStatus] = PublicationStatus.DRAFT
    is_active: Optional[bool] = True


class VideoUpdate(BaseModel):
    tibetan_title: Optional[str] = None
    english_title: Optional[str] = None
    tibetan_description: Optional[str] = None
    english_description: Optional[str] = None
    video_url: Optional[str] = None
    published_date: Optional[datetime] = None
    publication_status: Optional[PublicationStatus] = None
    is_active: Optional[bool] = None
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Video URL must start with http:// or https://')
        return v


class VideoPublish(BaseModel):
    published_date: Optional[datetime] = None


class VideoPublishResponse(BaseModel):
    success: bool
    message: str
    data: Optional["VideoResponse"] = None


class VideoResponse(VideoBase, TimestampMixin):
    id: int
    published_date: Optional[datetime] = None
    publication_status: PublicationStatus
    is_active: bool
    
    class Config:
        from_attributes = True


class AudioPaginatedResponse(PaginatedResponse):
    audio_files: List[AudioResponse]


class VideoPaginatedResponse(PaginatedResponse):
    videos: List[VideoResponse]