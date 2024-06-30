from typing import Annotated, Any

import boto3  # type: ignore [import-untyped]
from fastapi import HTTPException, status

from server.config import CONFIG
from server.services.interfaces.i_cognito_client import ICognitoClient


class CognitoClient(ICognitoClient):
    _aws_client: Any

    def __init__(self) -> None:
        self._aws_client = boto3.client(
            "cognito-idp",
            region_name=CONFIG.aws_region_name,
            aws_access_key_id=CONFIG.aws_access_key_id,
            aws_secret_access_key=CONFIG.aws_secret_access_key,
        )

    def get_username_by_token(self, token: str) -> str:
        try:
            cognito_user = self._aws_client.get_user(AccessToken=token)
        except Exception as e:
            print(e)
            raise AuthenticationError()
        username: str = cognito_user["Username"]
        return username

    def create_user(self, username: str, email: str) -> Annotated[str, "cognito_id"]:
        try:
            response = self._aws_client.admin_create_user(
                UserPoolId=CONFIG.aws_user_pool_id,
                Username=username,
                UserAttributes=[{"Name": "email", "Value": email}],
            )
            cognito_id: str = response["User"]["Attributes"][0]["Value"]
            return cognito_id
        except self._aws_client.exceptions.UsernameExistsException:
            raise UsernameAlreadyExists(username)

    def delete_user(self, username: str) -> None:
        self._aws_client.admin_delete_user(
            UserPoolId=CONFIG.aws_user_pool_id,
            Username=username,
        )


class AuthenticationError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Error on authentication")


class UsernameAlreadyExists(HTTPException):
    def __init__(self, username: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT, f"Username '{username}' already exists"
        )
