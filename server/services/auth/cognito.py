import boto3
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.config import CONFIG
from server.models.user import User

bearer_scheme = HTTPBearer()

aws_client = boto3.client(
    "cognito-idp",
    region_name=CONFIG.aws_region_name,
    aws_access_key_id=CONFIG.aws_access_key_id,
    aws_secret_access_key=CONFIG.aws_secret_access_key,
)


async def current_user(
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    token = auth.credentials
    try:
        cognito_user = aws_client.get_user(AccessToken=token)
    except Exception as e:
        print(e)
        raise HTTPException(401, "Error on authentication")
    user = await User.by_username(cognito_user["Username"])
    if user is None:
        raise HTTPException(404, "User not found")
    return user


async def current_admin_user(user: User = Depends(current_user)) -> User:
    if user.is_admin:
        return user
    raise HTTPException(403, "Admin access is required")


def create_cognito_user(username: str, email: str) -> str:
    try:
        response = aws_client.admin_create_user(
            UserPoolId=CONFIG.aws_user_pool_id,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
        cognito_id: str = response["User"]["Attributes"][0]["Value"]
        return cognito_id
    except aws_client.exceptions.UsernameExistsException:
        raise HTTPException(409, "Username already exists")


def delete_cognito_user(username: str) -> None:
    aws_client.admin_delete_user(
        UserPoolId=CONFIG.aws_user_pool_id,
        Username=username,
    )
