from typing import Annotated

from fastapi import APIRouter, Depends

from server.models.database.user_db_model import User
from server.services.auth.authenticate import authenticate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_current_user(user: Annotated[User, Depends(authenticate)]) -> User:
    return user
