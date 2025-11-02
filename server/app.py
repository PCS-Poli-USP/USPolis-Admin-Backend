"""Server app config."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.deps_overrides import DepsOverrides
from server.exception_handlers import add_exception_handlers
from server.middlewares import LoggerMiddleware
from server.routes.admin import router as AdminRouter
from server.routes.public import router as PublicRouter
from server.routes.authenticated import router as AuthenticatedRouter
from server.routes.restricted import router as RestrictedRouter

from server.config import CONFIG

app = FastAPI(
    title="USPolis Server",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggerMiddleware)

app.include_router(PublicRouter)
app.include_router(AuthenticatedRouter)
app.include_router(RestrictedRouter)
app.include_router(AdminRouter)

app.dependency_overrides = DepsOverrides

add_exception_handlers(app)
