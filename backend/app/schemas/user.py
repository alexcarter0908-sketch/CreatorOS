from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: EmailStr
    avatar_url: str | None
    is_active: bool
    is_superuser: bool


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None