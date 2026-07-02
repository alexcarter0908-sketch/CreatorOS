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

    def delete(
        self,
        user: User,
    ) -> None:
        self.db.delete(user)
        self.db.commit()