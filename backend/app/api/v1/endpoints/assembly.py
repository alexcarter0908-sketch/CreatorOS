from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.services.video_assembly.assembly_service import AssemblyService
from app.services.video_assembly.schemas import AssemblyRequest

router = APIRouter(
    prefix="/assembly",
    tags=["Video Assembly"],
)


@router.post("/render")
async def render_assembly(
    request: AssemblyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AssemblyService(db)
    asset = service.start_assembly(
        owner_id=current_user.id,
        request=request,
    )

    return {
        "asset_id": asset.id,
        "status": asset.status,
        "message": "Assembly started. Poll GET /assets/{asset_id} for progress.",
    }
