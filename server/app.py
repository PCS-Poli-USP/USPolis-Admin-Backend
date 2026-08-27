"""Server app config."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.deps_overrides import DepsOverrides
from server.exception_handlers import add_exception_handlers
from server.middlewares import LoggerMiddleware
from server.routes.admin import router as AdminRouter
from server.routes.public import router as PublicRouter
from server.routes.authenticated import router as AuthenticatedRouter
from server.routes.restricted import router as RestrictedRouter
from server.routes.health import router as HealthRouter
from server.routes.dev import router as DevRouter

from server.config import CONFIG
from server.cache import clear_expired_cache
from server.services.daily_tasks import run_daily_tasks
from server.utils.brazil_datetime import BrazilDatetime

_cleanup_task: asyncio.Task[None] | None = None  # Declaração explícita
_daily_tasks_task: asyncio.Task[None] | None = None


async def periodic_cache_cleanup() -> None:
    """Task que roda a cada 60 minutos limpando cache expirado"""
    while True:
        await asyncio.sleep(3600)
        count = clear_expired_cache()
        print(f"Cache cleanup: removed {count} expired entries")


async def periodic_daily_tasks() -> None:
    """Task que roda uma vez por dia, à meia-noite (horário de Brasília)"""
    while True:
        now = BrazilDatetime.now_utc()
        next_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        await asyncio.sleep((next_midnight - now).total_seconds())
        run_daily_tasks()
        print("Daily tasks ran")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação"""
    global _cleanup_task, _daily_tasks_task
    _cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    print("Cache cleanup started")
    _daily_tasks_task = asyncio.create_task(periodic_daily_tasks())
    print("Daily tasks scheduler started")

    yield

    # Shutdown
    if _cleanup_task:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
    print("Cache cleanup stoped")

    if _daily_tasks_task:
        _daily_tasks_task.cancel()
        try:
            await _daily_tasks_task
        except asyncio.CancelledError:
            pass
    print("Daily tasks scheduler stoped")


app = FastAPI(
    title="USPolis Server",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(LoggerMiddleware)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)

app.include_router(HealthRouter)
app.include_router(PublicRouter)
app.include_router(AuthenticatedRouter)
app.include_router(RestrictedRouter)
app.include_router(AdminRouter)

app.dependency_overrides = DepsOverrides

add_exception_handlers(app)

if CONFIG.environment == "development":
    app.include_router(DevRouter)
