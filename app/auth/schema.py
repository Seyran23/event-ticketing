from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr

from app.core.enums import Role
from app.users.schema import UserResponse


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    role: Role
    type: Literal["access", "refresh"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResult(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
