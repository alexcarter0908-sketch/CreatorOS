from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Asset
from app.database.session.database import get_db
from app.services.assets.asset_service import AssetService
from app.services.jobs.job_queue import job_queue
from app.services.video_assembly.assembler import VideoAssembler
from app.services.video_assembly.schemas import AssemblyRequest


class AssemblyService:
    def __init__(self, db: Session):
        self.db = db
        self.asset_service = AssetService(db)

    def start_assembly(
        self,
        *,
        owner_id: str,
        request: AssemblyRequest,
    ) -> Asset:
        asset = self.asset_service.start(
            owner_id=owner_id,
            asset_type=(
                "short_video" if request.height >= request.width else "long_video"
            ),
            provider="creatoros_assembly",
            model_id="ffmpeg",
            prompt=None,
            project_id=request.project_id,
        )

        job_queue.enqueue(
            lambda: self._run_assembly(asset.id, request)
        )

        return asset

    async def _run_assembly(
        self,
        asset_id: str,
        request: AssemblyRequest,
    ) -> None:
        db_gen = get_db()
        db = next(db_gen)

        try:
            service = AssetService(db)
            asset = service.repo.get_by_id(asset_id)

            if asset is None:
                return

            try:
                assembler = VideoAssembler()
                output_path = await assembler.assemble(request)

                file_bytes = output_path.read_bytes()

                service.complete(
                    asset,
                    file_bytes=file_bytes,
                    filename=output_path.name,
                    mime_type="video/mp4",
                )

            except Exception as exc:
                import traceback
                tb = traceback.format_exc()
                service.fail(asset, error_message=(repr(exc) + tb)[:4000])
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

