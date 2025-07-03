"""
Schemas package for the application.
Organized by domain/functionality for better maintainability.
"""

# Base schemas
from .base import TimestampMixin, PaginationResponse, PaginatedResponse

# Reference data schemas
from .reference import (
    SermonBase, SermonCreate, SermonResponse,
    YanaBase, YanaCreate, YanaResponse,
    TranslationTypeBase, TranslationTypeCreate, TranslationTypeResponse,
    EditionBase, EditionCreate, EditionUpdate, EditionResponse, EditionPaginatedResponse
)

# Category schemas
from .categories import (
    MainCategoryBase, MainCategoryCreate, MainCategoryUpdate, MainCategoryResponse,
    MainCategoryWithSubCategories,
    SubCategoryBase, SubCategoryCreate, SubCategoryCreateRequest, SubCategoryUpdate,
    SubCategoryResponse, SubCategoryWithTexts,MainCategoryLanguageResponse,SubCategoryLanguageResponse
)

# Text schemas
from .texts import (
    VolumeBase, VolumeCreate, VolumeUpdate, VolumeResponse,
    YesheDESpanBase, YesheDESpanCreate, YesheDESpanUpdate, YesheDESpanResponse,
    TextSummaryBase, TextSummaryCreate, TextSummaryUpdate, TextSummaryResponse,
    KagyurTextBase, KagyurTextCreate, KagyurTextCreateRequest, KagyurTextUpdate,
    KagyurTextResponse
)

# Media schemas
from .media import (
    AudioBase, AudioCreate, AudioUpdate, AudioResponse, AudioPaginatedResponse,
    VideoBase, VideoCreate, VideoUpdate, VideoPublish, VideoResponse, VideoPaginatedResponse
)

# News schemas
from .news import (
    NewsBase, NewsCreate, NewsUpdate, NewsPublish, NewsResponse, NewsPaginatedResponse
)

# User schemas
from .users import (
    UserBase, UserCreate, UserUpdate, UserResponse, PaginatedUsersResponse
)

# Auth schemas
from .auth import (
    LoginRequest, LoginResponse, RefreshResponse, LogoutResponse
)

# Search schemas
from .search import (
    SearchRequest, SearchSuggestionResponse, TextsListResponse,
    FilterOptionsResponse, KarchagStatsResponse
)

def _resolve_forward_refs():
    """Resolve forward references after all schemas are imported"""
    try:
        from .categories import SubCategoryWithTexts
        SubCategoryWithTexts.model_rebuild()
    except Exception:
        # If forward reference resolution fails, it's usually fine
        # The schemas will work without the resolved references
        pass

# Call the resolver
_resolve_forward_refs()

__all__ = [
    # Base
    "TimestampMixin", "PaginationResponse", "PaginatedResponse",
    
    # Reference
    "SermonBase", "SermonCreate", "SermonResponse",
    "YanaBase", "YanaCreate", "YanaResponse",
    "TranslationTypeBase", "TranslationTypeCreate", "TranslationTypeResponse",
    "EditionBase", "EditionCreate", "EditionUpdate", "EditionResponse", "EditionPaginatedResponse",
    
    # Category
    "MainCategoryBase", "MainCategoryCreate", "MainCategoryUpdate", "MainCategoryResponse",
    "MainCategoryWithSubCategories",
    "SubCategoryBase", "SubCategoryCreate", "SubCategoryCreateRequest", "SubCategoryUpdate",
    "SubCategoryResponse", "SubCategoryWithTexts","MainCategoryLanguageResponse","SubCategoryLanguageResponse",
    
    # Text
    "VolumeBase", "VolumeCreate", "VolumeUpdate", "VolumeResponse",
    "YesheDESpanBase", "YesheDESpanCreate", "YesheDESpanUpdate", "YesheDESpanResponse",
    "TextSummaryBase", "TextSummaryCreate", "TextSummaryUpdate", "TextSummaryResponse",
    "KagyurTextBase", "KagyurTextCreate", "KagyurTextCreateRequest", "KagyurTextUpdate",
    "KagyurTextResponse",
    
    # Media
    "AudioBase", "AudioCreate", "AudioUpdate", "AudioResponse", "AudioPaginatedResponse",
    "VideoBase", "VideoCreate", "VideoUpdate", "VideoPublish", "VideoResponse", "VideoPaginatedResponse",
    
    # News
    "NewsBase", "NewsCreate", "NewsUpdate", "NewsPublish", "NewsResponse", "NewsPaginatedResponse",
    
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "PaginatedUsersResponse",
    
    # Auth
    "LoginRequest", "LoginResponse", "RefreshResponse", "LogoutResponse",
    
    # Search
    "SearchRequest", "SearchSuggestionResponse", "TextsListResponse",
    "FilterOptionsResponse", "KarchagStatsResponse"
]