from fastapi import APIRouter

from server.deps.authenticate import UserDep
from server.models.http.responses.user_response_models import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_current_user(
    user: UserDep,
) -> UserResponse:
    """Get current user"""
    return UserResponse.from_user(user)