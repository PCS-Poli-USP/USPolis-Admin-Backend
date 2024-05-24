from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.deps.cognito_client import CognitoClientDep
from server.deps.session_dep import SessionDep
from server.models.database.user_db_model import User
from server.repositories.users_repository import UserRepository

security = HTTPBearer()


async def authenticate(
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


async def admin_authenticate(user: Annotated[User, Depends(authenticate)]) -> None:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User must be admin")

UserDep = Annotated[User, Depends(authenticate)]