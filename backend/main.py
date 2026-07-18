"""Application factory — creates and configures the FastAPI app."""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.middleware.logging import RequestLoggingMiddleware
from backend.middleware.errors import register_error_handlers

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ल Kanun API",
        description="Legal AI platform for Nepal and India — REST API",
        version="0.2.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    # ── Middleware (order matters: last added = first executed) ────────
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Error handlers ────────────────────────────────────────────────
    register_error_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────
    from backend.routers import router as auth_router
    from backend.routers.laws import router as laws_router
    from backend.routers.saved import router as saved_router
    from backend.routers.users import router as users_router
    from backend.routers.admin import router as admin_router
    from backend.routers.feedback import router as feedback_router

    prefix = settings.api_v1_prefix
    app.include_router(auth_router, prefix=prefix)
    app.include_router(laws_router, prefix=prefix)
    app.include_router(saved_router, prefix=prefix)
    app.include_router(users_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(feedback_router, prefix=prefix)

    # ── Health ────────────────────────────────────────────────────────
    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.2.0"}

    # ── Startup / shutdown ────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup():
        logger.info("starting_up", version="0.2.0")
        await init_db()
        logger.info("database_ready")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("shutting_down")

    return app


# Uvicorn entrypoint
app = create_app()
