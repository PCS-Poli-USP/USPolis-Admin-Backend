from fastapi import HTTPException

from server.config import CONFIG
from server.connections.aws import aws_client


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
