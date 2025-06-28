# schemas/__init__.py
from pydantic import BaseModel, ConfigDict, Field,validator
from datetime import datetime
from typing import List, Optional

# Base schemas for reference models
class SermonBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None

class SermonResponse(SermonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SermonCreate(SermonBase):
    pass

class YanaBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None

class YanaResponse(YanaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class YanaCreate(YanaBase):
    pass

class TranslationTypeBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None

class TranslationTypeCreate(TranslationTypeBase):
    pass

class TranslationTypeResponse(TranslationTypeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Volume schemas - for nested creation
class VolumeBase(BaseModel):
    volume_number: Optional[str] = None
    start_page: Optional[str] = None
    end_page: Optional[str] = None
    order_index: int = 0

class VolumeCreate(VolumeBase):
    """For creating volume within YesheDESpan (no yeshe_de_span_id needed)"""
    pass

class VolumeUpdate(VolumeBase):
    pass

class VolumeResponse(VolumeBase):
    id: int
    yeshe_de_span_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# YesheDESpan schemas - for nested creation
class YesheDESpanBase(BaseModel):
    pass

class YesheDESpanCreate(YesheDESpanBase):
    """For creating YesheDESpan within Text (no text_id needed)"""
    volumes: List[VolumeCreate] = Field(default_factory=list)

class YesheDESpanUpdate(YesheDESpanBase):
    volumes: Optional[List[VolumeCreate]] = None

class YesheDESpanResponse(BaseModel):
    id: int
    text_id: int
    created_at: datetime
    updated_at: datetime
    volumes: List[VolumeResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# Text Summary schemas
class TextSummaryBase(BaseModel):
    translator_homage_english: Optional[str] = None
    translator_homage_tibetan: Optional[str] = None
    purpose_english: Optional[str] = None
    purpose_tibetan: Optional[str] = None
    text_summary_english: Optional[str] = None
    text_summary_tibetan: Optional[str] = None
    keyword_and_meaning_english: Optional[str] = None
    keyword_and_meaning_tibetan: Optional[str] = None
    relation_english: Optional[str] = None
    relation_tibetan: Optional[str] = None
    question_and_answer_english: Optional[str] = None
    question_and_answer_tibetan: Optional[str] = None
    translator_notes_english: Optional[str] = None
    translator_notes_tibetan: Optional[str] = None

class TextSummaryCreate(TextSummaryBase):
    pass

class TextSummaryUpdate(TextSummaryBase):
    pass

class TextSummaryResponse(TextSummaryBase):
    id: int
    text_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Kagyur Text schemas
class KagyurTextBase(BaseModel):
    derge_id: Optional[str] = None
    yeshe_de_id: Optional[str] = None
    tibetan_title: Optional[str] = None
    chinese_title: Optional[str] = None
    sanskrit_title: Optional[str] = None
    english_title: Optional[str] = None
    sermon_id: Optional[int] = None
    yana_id: Optional[int] = None
    translation_type_id: Optional[int] = None
    order_index: int = 0
    is_active: bool = True

class KagyurTextCreate(KagyurTextBase):
    sub_category_id: int
    text_summary: Optional[TextSummaryCreate] = None
    yeshe_de_spans: List[YesheDESpanCreate] = Field(default_factory=list)
class KagyurTextCreateRequest(KagyurTextBase):
    text_summary: Optional[TextSummaryCreate] = None
    yeshe_de_spans: Optional[List[YesheDESpanCreate]] = Field(default_factory=list)
class KagyurTextUpdate(KagyurTextBase):
    text_summary: Optional[TextSummaryCreate] = None
    yeshe_de_spans: Optional[List[YesheDESpanCreate]] = None

class KagyurTextResponse(KagyurTextBase):
    id: int
    sub_category_id: int
    created_at: datetime
    updated_at: datetime
    text_summary: Optional[TextSummaryResponse] = None
    sermon: Optional[SermonResponse] = None
    yana: Optional[YanaResponse] = None
    yeshe_de_spans: List[YesheDESpanResponse] = []
    translation_type: Optional[TranslationTypeResponse] = None
    model_config = ConfigDict(from_attributes=True)



# Sub Category schemas
class SubCategoryBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None
    description_english: Optional[str] = None
    description_tibetan: Optional[str] = None
    order_index: int = 0
    is_active: bool = True

class SubCategoryCreate(SubCategoryBase):
    main_category_id: int

class SubCategoryCreateRequest(SubCategoryBase):
    pass

class SubCategoryUpdate(BaseModel):
    name_english: Optional[str] = None
    name_tibetan: Optional[str] = None
    description_english: Optional[str] = None
    description_tibetan: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class SubCategoryResponse(SubCategoryBase):
    id: int
    main_category_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SubCategoryWithTexts(SubCategoryResponse):
    texts: List[KagyurTextResponse] = []

# Main Category schemas
class MainCategoryBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None
    description_english: Optional[str] = None
    description_tibetan: Optional[str] = None
    order_index: int = 0
    is_active: bool = True

class MainCategoryCreate(MainCategoryBase):
    pass

class MainCategoryUpdate(MainCategoryBase):
    pass

class MainCategoryResponse(MainCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MainCategoryWithSubCategories(MainCategoryResponse):
    sub_categories: List[SubCategoryResponse] = []

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

class AudioResponse(AudioBase):
    id: int
    text_id: int
    audio_url: str
    file_name: str
    file_size: int
    duration: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


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

class NewsPublish(BaseModel):
    published_date: datetime

class NewsResponse(NewsBase):
    id: int
    published_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
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
    is_active: Optional[bool] = True

class VideoUpdate(BaseModel):
    tibetan_title: Optional[str] = None
    english_title: Optional[str] = None
    tibetan_description: Optional[str] = None
    english_description: Optional[str] = None
    video_url: Optional[str] = None
    published_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    
    @validator('video_url')
    def validate_video_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Video URL must start with http:// or https://')
        return v

class VideoPublish(BaseModel):
    published_date: datetime

class VideoResponse(VideoBase):
    id: int
    published_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False

# Properties to receive when creating a new user
class UserCreate(UserBase):
    password: str


# Properties to receive when updating a user
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None


# Properties to return via API (includes read-only fields)
class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    limit: int
    pages: int

class PaginationResponse(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_prev: bool

class TextsListResponse(BaseModel):
    texts: List[KagyurTextResponse]
    pagination: PaginationResponse

class FilterOptionsResponse(BaseModel):
    categories: List[MainCategoryBase]
    sermons: List[SermonBase]
    yanas: List[YanaBase]
    translation_types: List[TranslationTypeBase]
    language: str  # The language preference used
    
    model_config = ConfigDict(from_attributes=True)

# Search request schema (optional - for POST search if needed)
class SearchRequest(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    sermon_id: Optional[int] = None
    yana_id: Optional[int] = None
    translation_type_id: Optional[int] = None
    page: int = 1
    limit: int = 20
    language: str = "en"
    
    model_config = ConfigDict(from_attributes=True)

# Search suggestion response
class SearchSuggestionResponse(BaseModel):
    suggestions: List[str]
    query: str
    language: str
    
    model_config = ConfigDict(from_attributes=True)

# Stats response schema
class KarchagStatsResponse(BaseModel):
    total_texts: int
    total_categories: int
    total_sermons: int
    total_yanas: int
    total_translation_types: int
    texts_by_category: List[tuple]  # [(category_name, count), ...]
    texts_by_yana: List[tuple]      # [(yana_name, count), ...]
    
    model_config = ConfigDict(from_attributes=True)


class AudioPaginatedResponse(PaginatedResponse):
    audio_files: list[AudioResponse]

class NewsPaginatedResponse(PaginatedResponse):
    news_articles: list[NewsResponse]

class VideoPaginatedResponse(PaginatedResponse):
    videos: list[VideoResponse]

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    tokens: dict

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LogoutResponse(BaseModel):
    message: str

class PaginatedUsersResponse(BaseModel):
    users: List[UserResponse]
    pagination: dict

# Edition schemas
class EditionBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None
    description_english: Optional[str] = None
    description_tibetan: Optional[str] = None
    abbreviation: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    location: Optional[str] = None
    total_volumes: Optional[int] = None
    order_index: int = 0
    is_active: bool = True

class EditionCreate(EditionBase):
    pass

class EditionUpdate(BaseModel):
    name_english: Optional[str] = None
    name_tibetan: Optional[str] = None
    description_english: Optional[str] = None
    description_tibetan: Optional[str] = None
    abbreviation: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    location: Optional[str] = None
    total_volumes: Optional[int] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class EditionResponse(EditionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EditionPaginatedResponse(BaseModel):
    editions: List[EditionResponse]
    total: int
    page: int
    limit: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)