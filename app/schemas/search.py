from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .texts import KagyurTextResponse
from .base import PaginationResponse
from .reference import SermonBase, YanaBase, TranslationTypeBase
from .categories import MainCategoryBase


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


class SearchSuggestionResponse(BaseModel):
    suggestions: List[str]
    query: str
    language: str
    
    model_config = ConfigDict(from_attributes=True)


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


class KarchagStatsResponse(BaseModel):
    total_texts: int
    total_categories: int
    total_sermons: int
    total_yanas: int
    total_translation_types: int
    texts_by_category: List[tuple]  # [(category_name, count), ...]
    texts_by_yana: List[tuple]      # [(yana_name, count), ...]
    
    model_config = ConfigDict(from_attributes=True)

