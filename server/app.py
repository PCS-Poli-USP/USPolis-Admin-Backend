"""Server app config."""
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.deps_overrides import DepsOverrides
from server.exception_handlers import add_exception_handlers
from server.middlewares import LoggerMiddleware
from server.routes.admin import router as AdminRouter
from server.routes.admin import cookie_router as AdminCookieRouter
from server.routes.public import router as PublicRouter
from server.routes.authenticated import router as AuthenticatedRouter
from server.routes.restricted import router as RestrictedRouter
from server.routes.health import router as HealthRouter

from server.config import CONFIG
from server.cache import clear_expired_cache

_cleanup_task: asyncio.Task[None] | None = None  # Declaração explícita

async def periodic_cache_cleanup() -> None:
    """Task que roda a cada 60 minutos limpando cache expirado"""
    while True:
        await asyncio.sleep(3600)
        count = clear_expired_cache()
        print(f"Cache cleanup: removed {count} expired entries")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação"""
    global _cleanup_task
    _cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    print("Cache cleanup started")
    
    yield
    
    # Shutdown
    if _cleanup_task:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
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

app.include_router(HealthRouter)
app.include_router(PublicRouter)
app.include_router(AuthenticatedRouter)
app.include_router(RestrictedRouter)
app.include_router(AdminRouter)
app.include_router(AdminCookieRouter)

app.dependency_overrides = DepsOverrides

add_exception_handlers(app)
