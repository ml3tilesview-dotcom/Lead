from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, conversations, health
from app.config import get_settings
from app.logging_config import configure_logging

settings = get_settings()
configure_logging(debug=settings.debug)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN001
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI Lead Generation and Social Media Auto-Reply System — Phase 1",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(conversations.router)

    @app.get("/", tags=["root"])
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": "1.0.0",
            "phase": 1,
            "docs": "/docs",
            "health": "/health/live",
        }

    return app


app = create_app()
