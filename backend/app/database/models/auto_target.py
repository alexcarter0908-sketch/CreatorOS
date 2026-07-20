from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class AutoTarget(
    Base,
    BaseModelMixin,
):
    """
    Represents a recurring auto-generation target set by a user.

    Fully user-controlled schedule - nothing fixed:
      - interval_days: run every N days (1 = daily, 2 = every 2 days,
        3 = every 3 days, 7 = weekly, or any number the user picks).
      - run_at_hour / run_at_minute: what time of day to run, on the
        day it's due (0-23 / 0-59, user's choice).
    """

    __tablename__ = "auto_targets"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    interval_days: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    run_at_hour: Mapped[int] = mapped_column(
        Integer,
        default=9,
        nullable=False,
    )
    run_at_minute: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_run_date: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    auto_publish: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    platforms: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    tags: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    last_run_at: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    owner = relationship("User")
    project = relationship("Project")
