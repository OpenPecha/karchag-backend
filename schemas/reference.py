from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .base import TimestampMixin


class SermonBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None


class SermonCreate(SermonBase):
    pass


class SermonResponse(SermonBase, TimestampMixin):
    id: int
    model_config = ConfigDict(from_attributes=True)


class YanaBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None


class YanaCreate(YanaBase):
    pass


class YanaResponse(TimestampMixin, BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TranslationTypeBase(BaseModel):
    name_english: str
    name_tibetan: Optional[str] = None


class TranslationTypeCreate(TranslationTypeBase):
    pass


class TranslationTypeResponse(TranslationTypeBase, TimestampMixin):
    id: int
    model_config = ConfigDict(from_attributes=True)


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


class EditionResponse(EditionBase, TimestampMixin):
    id: int
    model_config = ConfigDict(from_attributes=True)


class EditionPaginatedResponse(BaseModel):
    editions: List[EditionResponse]
    total: int
    page: int
    limit: int
    pages: int
    model_config = ConfigDict(from_attributes=True)
