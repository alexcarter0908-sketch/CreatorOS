from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.database.session.database import SessionLocal
from app.repositories.auto_target_repository import AutoTargetRepository
from app.schemas.ai_request import AIRequest
from app.services.assets.asset_service import AssetService
from app.services.orchestrator.ai_orchestrator import AIOrchestrator
from app.services.orchestrator.full_pipeline import run_full_pipeline
from apscheduler.triggers.cron import CronTrigger
from app.services.reports.usage_report_service import run_monthly_usage_reports
from app.services.reports.daily_digest_service import run_daily_digest_emails

logger = logging.getLogger("auto_scheduler")

orchestrator = AIOrchestrator()
scheduler = BackgroundScheduler()


def run_due_targets() -> None:
    db = SessionLocal()
    try:
        repo = AutoTargetRepository(db)
        due_targets = repo.list_due()

        for target in due_targets:
            logger.info(
                "Running auto target %s (owner=%s, type=%s, every %sd @ %02d:%02d)",
                target.id,
                target.owner_id,
                target.asset_type,
                target.interval_days,
                target.run_at_hour,
                target.run_at_minute,
            )

            try:
                if target.asset_type == "video":
                    platforms = target.platforms.split(",") if target.platforms else None
                    tags = target.tags.split(",") if target.tags else []

                    result = asyncio.run(
                        run_full_pipeline(
                            db,
                            owner_id=target.owner_id,
                            prompt=target.prompt,
                            project_id=target.project_id,
                            auto_publish=target.auto_publish,
                            platforms=platforms,
                            tags=tags,
                            workflow_name=f"Auto: {target.prompt[:50]}",
                        )
                    )
                    if result["status"] != "completed":
                        logger.warning(
                            "Auto target %s pipeline ended with status=%s",
                            target.id,
                            result["status"],
                        )
                else:
                    asset_service = AssetService(db)
                    asset = asset_service.start(
                        owner_id=target.owner_id,
                        asset_type=target.asset_type,
                        provider="auto",
                        model_id="auto",
                        prompt=target.prompt,
                        project_id=target.project_id,
                    )
                    ai_request = AIRequest(
                        prompt=target.prompt,
                        asset_type=target.asset_type,
                        project_id=target.project_id,
                    )
                    single_result = asyncio.run(orchestrator.execute(ai_request))
                    asset_service.complete_from_provider_result(asset, single_result)

            except Exception:
                logger.exception("Auto target %s failed", target.id)

            repo.mark_run(target)
    finally:
        db.close()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(
            run_due_targets,
            "interval",
            minutes=5,
            id="auto_target_check",
            replace_existing=True,
        )
        scheduler.add_job(
            run_monthly_usage_reports,
            CronTrigger(day=1, hour=6, minute=0),
            id="monthly_usage_reports",
            replace_existing=True,
        )
        scheduler.add_job(
            run_daily_digest_emails,
            CronTrigger(hour=7, minute=0),
            id="daily_digest_emails",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Auto-target scheduler started (checks every 5 minutes).")
        logger.info("Monthly usage report job scheduled (1st of each month, 06:00).")
        logger.info("Daily digest email job scheduled (every day, 07:00).")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
