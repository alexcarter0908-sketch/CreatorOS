from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class PublishAccount(
    Base,
    BaseModelMixin,
):
    """
    Stores OAuth credentials for a connected social platform account
    (YouTube, Instagram, TikTok, Facebook, etc.) belonging to a user.
    """

    __tablename__ = "publish_accounts"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    account_label: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    external_account_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    access_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    token_expiry: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scopes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    owner = relationship("User")