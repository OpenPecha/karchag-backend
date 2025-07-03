from pydantic import BaseModel, ConfigDict
from typing import List, Optional,TYPE_CHECKING
if TYPE_CHECKING:
    from schemas.texts import KagyurTextResponse
from .base import TimestampMixin
from datetime import datetime


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


class MainCategoryResponse(MainCategoryBase, TimestampMixin):
    id: int
    model_config = ConfigDict(from_attributes=True)


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


class SubCategoryResponse(SubCategoryBase, TimestampMixin):
    id: int
    main_category_id: int
    model_config = ConfigDict(from_attributes=True)


# Forward reference - will be resolved when text.py is imported
class SubCategoryWithTexts(SubCategoryResponse):
    texts: List["KagyurTextResponse"] = []


class SubCategoryLanguageResponse(BaseModel):
    """Response model for language-specific sub-category data"""
    id: int
    main_category_id: int
    name: str  # Will be either English or Tibetan based on lang parameter
    description: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MainCategoryLanguageResponse(BaseModel):
    """Response model for language-specific category data"""
    id: int
    name: str  # Will be either English or Tibetan based on lang parameter
    description: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    sub_categories: List[SubCategoryLanguageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class MainCategoryWithSubCategories(MainCategoryLanguageResponse):
    sub_categories: List[SubCategoryLanguageResponse] = []