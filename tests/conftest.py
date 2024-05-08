"""Pytest fixtures."""

from collections.abc import AsyncIterator

import pytest_asyncio
from asgi_lifespan import LifespanManager
from decouple import config  # type: ignore [import-untyped]
from fastapi import FastAPI
from httpx import AsyncClient

from server.config import CONFIG
from server.models.database.user_db_model import User
from tests.utils.user_test_utils import get_test_admin_user

# Override config settings before loading the app
CONFIG.testing = True
CONFIG.mongo_uri = config(
    "TEST_MONGO_URI", default="mongodb://localhost:27017")  # type: ignore
CONFIG.mongo_db_name = config(
    "TEST_MONGO_DB_NAME", default="uspolis-test")  # type: ignore

from server import app  # noqa: E402


async def clear_database(server: FastAPI) -> None:
    """Empty the test database."""
    async for collection in await server.db.list_collections():  # type: ignore[attr-defined]
        await server.db[collection["name"]].delete_many({})  # type: ignore


@pytest_asyncio.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    """Async server client that handles lifespan and teardown."""
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as _client:  # type: ignore
            try:
                yield _client
            except Exception as exc:
                print(exc)
            finally:
                await clear_database(app)


@pytest_asyncio.fixture(autouse=False)
async def user() -> AsyncIterator[User]:
    user = await get_test_admin_user()
    yield user
