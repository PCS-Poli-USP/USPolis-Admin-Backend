from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.connections.aws import aws_client
from server.models.database.user_db_model import User

security = HTTPBearer()


async def admin_middleware(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> None:
    token = credentials.credentials
    try:
        cognito_user = aws_client.get_user(AccessToken=token)
    except Exception as e:
        print(e)
        raise HTTPException(401, "Error on authentication")
    user = await User.by_username(cognito_user["Username"])
    if user is None:
        raise HTTPException(404, "User not found")
    if not user.is_admin:
        raise HTTPException(403, "User must be admin")
    request.state.current_user = user
