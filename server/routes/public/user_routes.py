from typing import Annotated

from fastapi import APIRouter, Depends

from server.deps.authenticate import authenticate
from server.models.database.user_db_model import User
from server.models.http.responses.user_response_models import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model_by_alias=False)
async def get_current_user(
    user: Annotated[User, Depends(authenticate)],
) -> UserResponse:
    return await UserResponse.from_user(user)
