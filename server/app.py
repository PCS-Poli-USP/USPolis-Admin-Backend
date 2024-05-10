"""Server app config."""

from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.connections.mongo import database_singleton
from server.mocks.dependency_overrides import overrides
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.database.subject_db_model import Subject
from server.models.database.classroom_db_model import Classroom
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday

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
    await init_beanie(db, document_models=[User, Building, Subject, Classroom, HolidayCategory, Holiday])
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

app.dependency_overrides = overrides
