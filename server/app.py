"""Server app config."""

from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.connections.mongo import database_singleton
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User

DESCRIPTION = """
This API powers whatever I want to make

It supports:

- Account sign-up and management
- Something really cool that will blow your socks off
"""


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Initialize application services."""

    database_singleton.init_connection()
    db = database_singleton.get_instance()
    await init_beanie(db, document_models=[User, Building])
    app.db = db  # type: ignore [attr-defined]

    print("Startup complete")
    yield
    print("Shutdown complete")


app = FastAPI(
    title="USPolis Server",
    description=DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
