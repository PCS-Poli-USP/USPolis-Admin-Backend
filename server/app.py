"""Server app config."""

import asyncio
from collections.abc import AsyncGenerator
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
from server.routes.public.online_routes import router as OnlineRouter
from server.routes.admin.online_admin_routes import router as AdminOnlineRouter

from server.config import CONFIG
from server.cache import clear_expired_cache
from server.services.online_presence_service import (
    DIFF_FLUSH_INTERVAL_SECONDS,
    REAPER_INTERVAL_SECONDS,
    flush_pending_diff,
    reap_stale_connections,
)

_cleanup_task: asyncio.Task[None] | None = None  # Declaração explícita
_online_diff_task: asyncio.Task[None] | None = None
_online_reaper_task: asyncio.Task[None] | None = None


async def periodic_cache_cleanup() -> None:
    """Task que roda a cada 60 minutos limpando cache expirado"""
    while True:
        await asyncio.sleep(3600)
        count = clear_expired_cache()
        print(f"Cache cleanup: removed {count} expired entries")


async def periodic_online_diff_flush() -> None:
    """Flushes batched online-presence diffs to admin listeners."""
    while True:
        await asyncio.sleep(DIFF_FLUSH_INTERVAL_SECONDS)
        await flush_pending_diff()


async def periodic_online_reaper() -> None:
    """Drops online connections that stopped heartbeating."""
    while True:
        await asyncio.sleep(REAPER_INTERVAL_SECONDS)
        await reap_stale_connections()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação"""
    global _cleanup_task, _online_diff_task, _online_reaper_task
    _cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    _online_diff_task = asyncio.create_task(periodic_online_diff_flush())
    _online_reaper_task = asyncio.create_task(periodic_online_reaper())
    print("Cache cleanup started")

    yield

    # Shutdown
    for task in (_cleanup_task, _online_diff_task, _online_reaper_task):
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    print("Cache cleanup stoped")


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

# Mounted directly (not via the public/admin tier __init__.py aggregators):
# those attach Request-based HTTP auth dependencies at router level, which
# break WS routes. See the WS-native auth in server/deps/authenticate.py.
app.include_router(OnlineRouter)
app.include_router(AdminOnlineRouter)

app.dependency_overrides = DepsOverrides

add_exception_handlers(app)

if CONFIG.environment == "development":
    app.include_router(DevRouter)
