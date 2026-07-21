from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotificationRepository(db)
    notifications = repo.list_by_owner(current_user.id)
    return NotificationListResponse(
        notifications=notifications,
        unread_count=repo.count_unread(current_user.id),
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotificationRepository(db)
    notification = repo.mark_read(current_user.id, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return notification


@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    NotificationRepository(db).mark_all_read(current_user.id)
    return {"detail": "All notifications marked as read."}
