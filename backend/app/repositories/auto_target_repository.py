from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.models import AutoTarget


class AutoTargetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        owner_id: str,
        asset_type: str,
        prompt: str,
        project_id: str | None = None,
        interval_days: int = 1,
        run_at_hour: int = 9,
        run_at_minute: int = 0,
        auto_publish: bool = True,
        platforms: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> AutoTarget:
        target = AutoTarget(
            owner_id=owner_id,
            project_id=project_id,
            asset_type=asset_type,
            prompt=prompt,
            interval_days=max(1, interval_days),
            run_at_hour=run_at_hour,
            run_at_minute=run_at_minute,
            auto_publish=auto_publish,
            platforms=",".join(platforms) if platforms else None,
            tags=",".join(tags) if tags else None,
            is_active=True,
        )
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target

    def list_by_owner(self, owner_id: str) -> list[AutoTarget]:
        return (
            self.db.query(AutoTarget)
            .filter(AutoTarget.owner_id == owner_id)
            .order_by(AutoTarget.created_at.desc())
            .all()
        )

    def get_by_id(self, target_id: str) -> AutoTarget | None:
        return self.db.query(AutoTarget).filter(AutoTarget.id == target_id).first()

    def deactivate(self, target: AutoTarget) -> AutoTarget:
        target.is_active = False
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target

    def activate(self, target: AutoTarget) -> AutoTarget:
        target.is_active = True
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target

    def delete(self, target: AutoTarget) -> None:
        self.db.delete(target)
        self.db.commit()

    def _local_now(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            hours=settings.DEFAULT_TIMEZONE_OFFSET_HOURS
        )

    def list_due(self) -> list[AutoTarget]:
        """
        A target is due when:
          - it has never run (first run happens immediately), or
          - today's local date >= (last_run_date + interval_days)
            AND local time-of-day >= run_at_hour:run_at_minute.

        This covers daily (interval_days=1), every-N-days, weekly
        (interval_days=7), or any custom cadence the user picked -
        nothing about the schedule is hardcoded here.
        """
        due: list[AutoTarget] = []
        local_now = self._local_now()

        targets = (
            self.db.query(AutoTarget)
            .filter(AutoTarget.is_active.is_(True))
            .all()
        )

        for target in targets:
            if target.last_run_date is None:
                due.append(target)
                continue

            last_date = datetime.fromisoformat(target.last_run_date).date()
            next_due_date = last_date + timedelta(days=target.interval_days)

            scheduled_dt = datetime.combine(
                next_due_date,
                local_now.time().replace(
                    hour=target.run_at_hour,
                    minute=target.run_at_minute,
                    second=0,
                    microsecond=0,
                ),
            )

            if local_now.replace(tzinfo=None) >= scheduled_dt:
                due.append(target)

        return due

    def mark_run(self, target: AutoTarget) -> AutoTarget:
        now_utc = datetime.now(timezone.utc)
        local_now = self._local_now()
        target.last_run_at = now_utc.isoformat()
        target.last_run_date = local_now.date().isoformat()
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target
