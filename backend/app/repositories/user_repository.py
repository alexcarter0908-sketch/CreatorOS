from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        user_id: str,
    ) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email.lower())
            .first()
        )

    def create(
        self,
        *,
        full_name: str,
        email: str,
        password_hash: str,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email.lower(),
            password_hash=password_hash,
            is_email_verified=False,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update(
        self,
        user: User,
    ) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def set_otp(
        self,
        user: User,
        *,
        otp_code: str,
        expires_at,
    ) -> User:
        user.otp_code = otp_code
        user.otp_expires_at = expires_at
        return self.update(user)

    def clear_otp(
        self,
        user: User,
    ) -> User:
        user.otp_code = None
        user.otp_expires_at = None
        return self.update(user)

    def mark_email_verified(
        self,
        user: User,
    ) -> User:
        user.is_email_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        return self.update(user)

    def delete(
        self,
        user: User,
    ) -> None:
        self.db.delete(user)
        self.db.commit()

    def get_by_google_id(
        self,
        google_id: str,
    ) -> User | None:
        return (
            self.db.query(User)
            .filter(User.google_id == google_id)
            .first()
        )

    def create_google_user(
        self,
        *,
        full_name: str,
        email: str,
        google_id: str,
        avatar_url: str | None = None,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email.lower(),
            password_hash=None,
            google_id=google_id,
            avatar_url=avatar_url,
            is_email_verified=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user