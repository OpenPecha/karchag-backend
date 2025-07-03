from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class TimestampMixin:
    """Mixin for models with timestamps"""
    created_at: datetime
    updated_at: datetime


class PaginationResponse(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    limit: int
    pages: int

