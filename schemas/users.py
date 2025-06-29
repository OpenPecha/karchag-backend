from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .base import TimestampMixin


class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase, TimestampMixin):
    id: int
    last_login: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class PaginatedUsersResponse(BaseModel):
    users: List[UserResponse]
    pagination: dict
