from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class Project(
    Base,
    BaseModelMixin,
):
    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )

    # When True, the system is free to move `status` forward automatically
    # based on project activity (e.g. draft -> active once content exists).
    # Set to False as soon as a user manually picks a status, so the system
    # never fights a deliberate choice.
    status_auto: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    brand_voice: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    owner = relationship(
        "User",
        back_populates="projects",
    )
