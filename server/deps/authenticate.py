from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.deps.cognito_client import CognitoClientDep
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingRepository
from server.repositories.user_repository import UserRepository

security = HTTPBearer()


def authenticate(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    cognito_client: CognitoClientDep,
    session: SessionDep,
) -> User:
    token = credentials.credentials
    username = cognito_client.get_username_by_token(token)
    user: User = UserRepository.get_by_username(username=username, session=session)
    request.state.current_user = user
    return user


def admin_authenticate(user: Annotated[User, Depends(authenticate)]) -> None:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User must be admin")


# -- permission authentications :


def building_authenticate(
    user: Annotated[User, Depends(authenticate)], session: SessionDep, building_id: Annotated[int, Header()]
) -> Building:
    building = BuildingRepository.get_by_id(id=building_id, session=session)
    if user.is_admin:
        return building
    if user.buildings is None or building not in user.buildings:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "User must have access to building"
        )
    return building


# exports:
UserDep = Annotated[User, Depends(authenticate)]
BuildingDep = Annotated[Building, Depends(building_authenticate)]
