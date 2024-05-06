from datetime import datetime

import pytest
from httpx import AsyncClient

from server.models.database.user_db_model import User


@pytest.mark.asyncio
async def test_user_get(client: AsyncClient) -> None:
    """Test user endpoint returns authorized user."""
    new_user = User(
        buildings=None,
        cognito_id="",
        created_by=None,
        email="henriqueduran15@gmail.com",
        is_admin=True,
        name="Henrique",
        updated_at=datetime.now(),
        username="hfduran",
    )
    await new_user.create()
    resp = await client.get("/user")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == new_user.email
