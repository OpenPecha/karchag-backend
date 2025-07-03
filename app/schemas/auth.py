from pydantic import BaseModel
from .users import UserResponse


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
