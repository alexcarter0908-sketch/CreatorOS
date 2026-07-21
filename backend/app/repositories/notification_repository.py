from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        owner_id: str,
        type: str,
        title: str,
        message: str | None = None,
        workflow_id: str | None = None,
    ) -> Notification:
        notification = Notification(
            owner_id=owner_id,
            type=type,
            title=title,
            message=message,
            workflow_id=workflow_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_by_owner(self, owner_id: str, limit: int = 30) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.owner_id == owner_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    def count_unread(self, owner_id: str) -> int:
        return (
            self.db.query(func.count(Notification.id))
            .filter(Notification.owner_id == owner_id, Notification.is_read.is_(False))
            .scalar()
            or 0
        )

    def mark_read(self, owner_id: str, notification_id: str) -> Notification | None:
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.owner_id == owner_id)
            .first()
        )
        if notification is None:
            return None
        notification.is_read = True
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_read(self, owner_id: str) -> None:
        (
            self.db.query(Notification)
            .filter(Notification.owner_id == owner_id, Notification.is_read.is_(False))
            .update({"is_read": True})
        )
        self.db.commit()
