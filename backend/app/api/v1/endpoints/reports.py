from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.models import User, UsageReport
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("")
async def list_usage_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(UsageReport)
        .filter(UsageReport.user_id == current_user.id)
        .order_by(UsageReport.period_start.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "month_label": r.month_label,
            "period_start": r.period_start,
            "period_end": r.period_end,
            "total_generations": r.total_generations,
            "failed_generations": r.failed_generations,
            "credits_spent": r.credits_spent,
            "credits_purchased": r.credits_purchased,
            "current_balance": r.current_balance,
            "breakdown": r.breakdown,
        }
        for r in reports
    ]