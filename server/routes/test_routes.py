from typing import Any

from fastapi import APIRouter, Body, Depends

from server.models.database.user_db_model import User
from server.services.current_user.current_user import get_current_user

router = APIRouter(prefix="/test", tags=["Test"])

embed = Body(..., embed=True)


@router.get("")
async def test(user: User = Depends(get_current_user)) -> Any:
    return {"hello": "world"}
