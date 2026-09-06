from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.enums import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        """Validate password."""
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "@$!%*?&" for char in value):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return value


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: Role
    must_change_password: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
