"""Server app config."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.deps.mocks.deps_overrides import DepsOverrides
from server.exception_handlers import add_exception_handlers
from server.routes.admin import router as AdminRouter
from server.routes.public import router as PublicRouter

app = FastAPI(
    title="USPolis Server",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AdminRouter)
app.include_router(PublicRouter)

app.dependency_overrides = DepsOverrides

add_exception_handlers(app)
