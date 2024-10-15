from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.deps.authenticate import GoogleAuthenticate

from server.repositories.user_repository import UserRepository

from server.models.http.requests.user_request_models import UserRegister


router = APIRouter(prefix="/users", tags=["Users", "Public"])
embed = Body(..., embed=True)


@router.post("/register")
def register(user_info: GoogleAuthenticate, session: SessionDep, username: str = embed) -> None:
    user_in = UserRegister(
        building_ids=[],
        email=user_info.email,
        is_admin=False,
        name=user_info.name,
        username=username
    )
    UserRepository.create(
        creator=None,
        cognito_client=None,
        session=session,
        user_in=user_in
    )
