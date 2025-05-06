from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user update."""

    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8)


class UserInDB(UserBase):
    """Schema for user in database."""

    id: int
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user response."""


class Token(BaseModel):
    """Schema for access token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""

    username: str | None = None
    scopes: list[str] = []
