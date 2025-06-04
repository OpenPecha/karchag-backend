# schemas/__init__.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

# Base schemas for reference models
class SermonBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None

class SermonResponse(SermonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class YanaBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None

class YanaResponse(YanaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TranslationTypeBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None

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

class KagyurTextUpdate(KagyurTextBase):
    pass

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

class SubCategoryUpdate(SubCategoryBase):
    pass

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

class AudioResponse(BaseModel):
    id: int
    text_id: int
    audio_url: str
    file_name: str
    file_size: int
    duration: int
    narrator_name_english: Optional[str]
    narrator_name_tibetan: Optional[str]
    audio_quality: str
    audio_language: str
    is_active: bool
    order_index: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class NewsResponse(BaseModel):
    id: int
    tibetan_title: Optional[str]
    english_title: Optional[str]
    tibetan_content: Optional[str]
    english_content: Optional[str]
    published_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class VideoResponse(BaseModel):
    id: int
    tibetan_title: Optional[str]
    english_title: Optional[str]
    tibetan_description: Optional[str]
    english_description: Optional[str]
    video_url: str
    published_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    limit: int
    pages: int