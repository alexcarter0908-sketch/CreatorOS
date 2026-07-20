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

    return {
        "status": "healthy",
        "available_providers": provider_manager.available_providers(),
        "health": await provider_manager.health_report(),
    }