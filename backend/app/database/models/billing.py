from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class BillingAccount(Base, BaseModelMixin):
    """One-to-one with User. Tracks credit balance and daily free quotas."""

    __tablename__ = "billing_accounts"
    __table_args__ = (
        CheckConstraint(
            "credit_balance >= 0",
            name="ck_billing_accounts_credit_balance_non_negative",
        ),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    credit_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Free-tier daily quota tracking (e.g. for "script")
    free_quota_used_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    free_quota_date: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "YYYY-MM-DD"

    user = relationship("User")


class CreditTransaction(Base, BaseModelMixin):
    """Append-only ledger of every credit movement (audit trail)."""

    __tablename__ = "credit_transactions"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # purchase | consumption | refund | bonus
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # positive = added, negative = spent
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    paddle_transaction_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

    user = relationship("User")
