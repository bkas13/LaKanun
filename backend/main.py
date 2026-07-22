"""Application factory — creates and configures the FastAPI app."""

import time

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.middleware.logging import RequestLoggingMiddleware
from backend.middleware.errors import register_error_handlers

_start_time = time.time()

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
    from backend.routers.rights import router as rights_router
    from backend.routers.issues import router as issues_router
    from backend.routers.ai_tools import router as ai_tools_router

    prefix = settings.api_v1_prefix
    app.include_router(auth_router, prefix=prefix)
    app.include_router(laws_router, prefix=prefix)
    app.include_router(saved_router, prefix=prefix)
    app.include_router(users_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(feedback_router, prefix=prefix)
    app.include_router(rights_router, prefix=prefix)
    app.include_router(issues_router, prefix=prefix)
    app.include_router(ai_tools_router, prefix=prefix)

    # ── Health ────────────────────────────────────────────────────────
    @app.get("/health")
    async def health():
        import os
        import time

        from backend.database import async_session
        from sqlalchemy import text

        uptime = time.time() - _start_time
        pid = os.getpid()

        # Process stats (psutil optional)
        mem_mb = None
        cpu_pct = None
        child_count = None
        try:
            import psutil
            proc = psutil.Process(pid)
            mem_mb = round(proc.memory_info().rss / 1024 / 1024, 1)
            cpu_pct = proc.cpu_percent(interval=0)
            child_count = len(proc.children(recursive=True))
        except ImportError:
            pass

        # DB connectivity check
        db_ok = False
        try:
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
                db_ok = True
        except Exception:
            pass

        return {
            "status": "ok" if db_ok else "degraded",
            "version": "0.2.0",
            "uptime_seconds": round(uptime, 1),
            "pid": pid,
            "db_connected": db_ok,
            "memory_mb": mem_mb,
            "cpu_percent": cpu_pct,
            "child_processes": child_count,
        }

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
