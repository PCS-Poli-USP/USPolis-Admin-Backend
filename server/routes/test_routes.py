from typing import Any

from fastapi import APIRouter, Body, Depends

from server.models.database.user_db_model import User
from server.services.auth.authenticate import authenticate

router = APIRouter(prefix="/test", tags=["Test"], dependencies=[Depends(authenticate)])

embed = Body(..., embed=True)


@router.get("")
async def test(user: User = Depends(authenticate)) -> Any:
    return {"hello": "world"}
