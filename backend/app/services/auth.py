from __future__ import annotations

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, db):
        self.users = UserRepository(db)

    def register(
        self,
        request: RegisterRequest,
    ):
        existing = self.users.get_by_email(request.email)

        if existing:
            raise ValueError("Email already registered.")

        password_hash = hash_password(request.password)

        return self.users.create(
            full_name=request.full_name,
            email=request.email,
            password_hash=password_hash,
        )

    def login(
        self,
        email: str,
        password: str,
    ) -> str:

        user = self.users.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password.")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password.")

        return create_access_token(
            subject=str(user.id),
        )