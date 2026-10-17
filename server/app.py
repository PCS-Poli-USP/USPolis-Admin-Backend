"""Server app config."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.deps_overrides import DepsOverrides
from server.exception_handlers import add_exception_handlers
from server.middlewares import (
    ApiKeyMiddleware,
    LoggerMiddleware,
    PartnerCorsMiddleware,
    RateLimitMiddleware,
)
from server.routes.admin import router as AdminRouter
from server.routes.public import router as PublicRouter
from server.routes.authenticated import router as AuthenticatedRouter
from server.routes.restricted import router as RestrictedRouter
from server.routes.health import router as HealthRouter
from server.routes.dev import router as DevRouter

from server.config import CONFIG
from server.services.cron.scheduler import lifespan

app = FastAPI(
    title="USPolis Server",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api",
    lifespan=lifespan,
)

# Middlewares run outermost-last-added:
#   Logger -> PartnerCors -> CORS -> ApiKey -> RateLimit -> app.
# ApiKey and RateLimit sit inside CORS so their 401/403/429 still carry CORS
# headers (otherwise the browser reports a CORS error instead). ApiKey runs
# before RateLimit so a valid key is counted against its own limits.
# PartnerCors sits outside CORS because CORSMiddleware rejects the preflight
# of any origin not in ALLOWED_ORIGINS; it serves browser-key origins
# (GET/HEAD on public routes, no credentials).
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ApiKeyMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Retry-After",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
)


app.add_middleware(PartnerCorsMiddleware)

app.add_middleware(LoggerMiddleware)

app.include_router(HealthRouter)
app.include_router(PublicRouter)
app.include_router(AuthenticatedRouter)
app.include_router(RestrictedRouter)
app.include_router(AdminRouter)

app.dependency_overrides = DepsOverrides

add_exception_handlers(app)

if CONFIG.environment == "development":
    app.include_router(DevRouter)
