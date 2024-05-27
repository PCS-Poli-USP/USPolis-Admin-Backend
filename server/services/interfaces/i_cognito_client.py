from abc import ABC, abstractmethod
from typing import Annotated


class ICognitoClient(ABC):
    @abstractmethod
    def get_username_by_token(self, token: str) -> str:
        pass

    @abstractmethod
    def create_user(self, username: str, email: str) -> Annotated[str, "cognito_id"]:
        pass

    @abstractmethod
    def delete_user(self, username: str) -> None:
        pass
