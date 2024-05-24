from typing import Annotated

from server.config import CONFIG
from server.deps.interfaces.i_cognito_client import ICognitoClient


class CognitoClientMock(ICognitoClient):
    def get_username_by_token(self, token: str) -> str:
        return CONFIG.mock_username

    def create_user(self, username: str, email: str) -> Annotated[str, "cognito_id"]:
        return "123"

    def delete_user(self, username: str) -> None:
        pass
