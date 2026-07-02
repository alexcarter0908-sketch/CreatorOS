from __future__ import annotations

from app.database.models import User
from app.schemas.user import UpdateProfileRequest


class UserService:
    def update_profile(
        self,
        user: User,
        request: UpdateProfileRequest,
    ) -> User:

        if request.full_name is not None:
            user.full_name = request.full_name

        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url

        return user