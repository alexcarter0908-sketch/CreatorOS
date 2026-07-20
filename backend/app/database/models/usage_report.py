from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.database.mixins import BaseModelMixin


class UsageReport(Base, BaseModelMixin):
    """
    One saved snapshot per user per month - built and stored once by
    run_monthly_usage_reports() so the dashboard "Reports" page can show
    history without recalculating from raw tables every time. The
    numbers themselves still always came from the live Assets/
    CreditTransaction tables at generation time - this is just a saved
    copy of that calculation, not a separate source of truth.
    """
    __tablename__ = "usage_reports"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month_label: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "July 2026"
    period_start: Mapped[str] = mapped_column(String(30), nullable=False)  # ISO date
    period_end: Mapped[str] = mapped_column(String(30), nullable=False)  # ISO date
    total_generations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_generations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits_purchased: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    breakdown: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    user = relationship("User")