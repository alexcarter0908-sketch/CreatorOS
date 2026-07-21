from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.database.models import User, Asset

logger = logging.getLogger("usage_reports")


def _yesterday_range(reference: datetime | None = None) -> tuple[datetime, datetime, str]:
    ref = reference or datetime.now(timezone.utc)
    start_of_today = ref.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_yesterday = start_of_today - timedelta(days=1)
    label = start_of_yesterday.strftime("%B %d, %Y")
    return start_of_yesterday, start_of_today, label


def run_daily_digest_emails() -> None:
    """
    Entry point called by the scheduler every morning. Emails a digest
    of yesterday's activity to every user who opted in via
    notify_email_digest AND actually had activity - users with zero
    generations are skipped so they don't get an empty email daily.
    """
    from app.database.session.database import SessionLocal
    from app.services.reports.usage_report_service import build_usage_summary
    from app.services.reports.usage_report_email import send_daily_digest_email

    db = SessionLocal()
    try:
        start, end, day_label = _yesterday_range()

        active_user_ids = {
            row[0]
            for row in db.query(Asset.owner_id)
            .filter(Asset.created_at >= start, Asset.created_at < end)
            .distinct()
            .all()
        }

        if not active_user_ids:
            return

        opted_in_users = (
            db.query(User)
            .filter(User.id.in_(active_user_ids), User.notify_email_digest.is_(True))
            .all()
        )

        for user in opted_in_users:
            try:
                summary = build_usage_summary(db, user.id, start, end)
                send_daily_digest_email(user.email, user.full_name, day_label, summary)
            except Exception:
                logger.exception("Failed to send daily digest to %s", user.email)
    finally:
        db.close()
