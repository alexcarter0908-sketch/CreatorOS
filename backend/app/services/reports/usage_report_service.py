from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import User, Asset, UsageReport
from app.database.models.billing import BillingAccount, CreditTransaction

logger = logging.getLogger("usage_reports")

ASSET_TYPE_LABELS = {
    "text": "Chat / Text Replies",
    "script": "Scripts",
    "seo": "SEO Packages",
    "document": "Documents",
    "image": "Images / Thumbnails",
    "video": "Videos",
    "audio": "Voiceovers",
    "research": "Research Reports",
}


def _previous_month_range(reference: datetime | None = None) -> tuple[datetime, datetime, str]:
    """
    Returns (start, end, label) for the full calendar month BEFORE the
    reference date (defaults to now) - e.g. if run on Aug 1st, this
    returns July 1st 00:00 to Aug 1st 00:00, labeled "July 2026".
    """
    ref = reference or datetime.now(timezone.utc)
    first_of_this_month = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_last_day = first_of_this_month - timedelta(days=1)
    first_of_prev_month = prev_month_last_day.replace(day=1)
    label = first_of_prev_month.strftime("%B %Y")
    return first_of_prev_month, first_of_this_month, label


def build_usage_summary(db: Session, user_id: str, start: datetime, end: datetime) -> dict:
    """
    Builds one user's usage summary for the given date range, reading
    live from the Assets table and the CreditTransaction ledger - never
    from hardcoded pricing numbers, so this automatically reflects
    whatever the current billing/credit rules were at the time each
    transaction actually happened.
    """
    asset_counts = (
        db.query(Asset.asset_type, func.count(Asset.id))
        .filter(
            Asset.owner_id == user_id,
            Asset.created_at >= start,
            Asset.created_at < end,
        )
        .group_by(Asset.asset_type)
        .all()
    )
    counts_by_type = {asset_type: count for asset_type, count in asset_counts}

    failed_count = (
        db.query(func.count(Asset.id))
        .filter(
            Asset.owner_id == user_id,
            Asset.created_at >= start,
            Asset.created_at < end,
            Asset.status == "failed",
        )
        .scalar()
    ) or 0

    credits_spent_raw = (
        db.query(func.coalesce(func.sum(CreditTransaction.amount), 0))
        .filter(
            CreditTransaction.user_id == user_id,
            CreditTransaction.type == "consumption",
            CreditTransaction.created_at >= start,
            CreditTransaction.created_at < end,
        )
        .scalar()
    ) or 0
    credits_spent = abs(int(credits_spent_raw))

    credits_purchased_raw = (
        db.query(func.coalesce(func.sum(CreditTransaction.amount), 0))
        .filter(
            CreditTransaction.user_id == user_id,
            CreditTransaction.type == "purchase",
            CreditTransaction.created_at >= start,
            CreditTransaction.created_at < end,
        )
        .scalar()
    ) or 0
    credits_purchased = int(credits_purchased_raw)

    account = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    current_balance = account.credit_balance if account else 0

    total_generations = sum(counts_by_type.values())

    breakdown = [
        {
            "asset_type": asset_type,
            "label": ASSET_TYPE_LABELS.get(asset_type, asset_type.title()),
            "count": count,
        }
        for asset_type, count in sorted(counts_by_type.items(), key=lambda x: -x[1])
    ]

    return {
        "total_generations": total_generations,
        "failed_generations": failed_count,
        "breakdown": breakdown,
        "credits_spent": credits_spent,
        "credits_purchased": credits_purchased,
        "current_balance": current_balance,
    }


def run_monthly_usage_reports() -> None:
    """
    Entry point called by the scheduler on the 1st of every month.
    Builds and emails a usage report for every user who had at least
    one generation in the just-completed month - users with zero
    activity are skipped so they don't get an empty report.
    """
    from app.database.session.database import SessionLocal
    from app.services.reports.usage_report_email import send_monthly_usage_report_email

    db = SessionLocal()
    try:
        start, end, month_label = _previous_month_range()

        active_user_ids = [
            row[0]
            for row in db.query(Asset.owner_id)
            .filter(Asset.created_at >= start, Asset.created_at < end)
            .distinct()
            .all()
        ]

        for user_id in active_user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                continue
            try:
                summary = build_usage_summary(db, user_id, start, end)

                existing = (
                    db.query(UsageReport)
                    .filter(UsageReport.user_id == user_id, UsageReport.month_label == month_label)
                    .first()
                )
                if existing is None:
                    db.add(
                        UsageReport(
                            user_id=user_id,
                            month_label=month_label,
                            period_start=start.isoformat(),
                            period_end=end.isoformat(),
                            total_generations=summary["total_generations"],
                            failed_generations=summary["failed_generations"],
                            credits_spent=summary["credits_spent"],
                            credits_purchased=summary["credits_purchased"],
                            current_balance=summary["current_balance"],
                            breakdown=summary["breakdown"],
                        )
                    )
                    db.commit()

                if getattr(user, "email", None):
                    send_monthly_usage_report_email(
                        user.email,
                        getattr(user, "full_name", "") or "",
                        month_label,
                        summary,
                    )
                    logger.info("Sent monthly usage report to %s for %s", user.email, month_label)
            except Exception:
                db.rollback()
                logger.exception("Failed to process monthly usage report for user %s", user_id)
    finally:
        db.close()