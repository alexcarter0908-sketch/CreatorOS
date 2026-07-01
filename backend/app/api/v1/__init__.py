from fastapi import APIRouter

from app.api.v1.endpoints.projects import router as projects_router
from app.api.v1.endpoints.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(
    projects_router,
    prefix="/projects",
    tags=["Projects"],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)