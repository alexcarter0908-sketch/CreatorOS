from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class Notification(Base, BaseModelMixin):
    __tablename__ = "notifications"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False, default="project_completed")

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    workflow_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
