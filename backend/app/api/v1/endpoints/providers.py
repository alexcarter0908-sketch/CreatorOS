from fastapi import APIRouter

from app.services.providers.manager.provider_manager import (
    ProviderManager,
)

router = APIRouter(
    prefix="/providers",
    tags=["Providers"],
)

provider_manager = ProviderManager()


@router.get("/health")
async def provider_health():

    selection = provider_manager.select(
        task="text",
    )

    return {
        "status": "healthy",
        "default_provider": selection.provider,
        "default_model": selection.model,
        "reason": selection.reason,
    }