from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
    email: EmailStr
    avatar_url: str | None
    is_active: bool
    is_superuser: bool
    is_email_verified: bool
    notify_email_digest: bool
    notify_low_credit_email: bool
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
    notify_email_digest: bool | None = None
    notify_low_credit_email: bool | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class DeleteAccountRequest(BaseModel):
    password: str | None = None
