from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.models.database.user_db_model import User
from server.services.cognito.cognito_client import CognitoClient

security = HTTPBearer()


async def authenticate(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    cognito_client: Annotated[CognitoClient, Depends()],
) -> User:
    token = credentials.credentials
    username = cognito_client.get_username_by_token(token)
    user: User | None = await User.by_username(username)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    request.state.current_user = user
    return user


async def admin_authenticate(user: Annotated[User, Depends(authenticate)]) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User must be admin")
    return user
