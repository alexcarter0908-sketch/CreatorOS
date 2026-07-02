from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import (
    auth_router,
    users_router,
    projects_router,
)
from app.core.config.settings import settings
from app.database.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CreatorOS Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    users_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    projects_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get(
    "/health",
    tags=["System"],
)
async def health():
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }