import traceback
import requests
from typing import Any
from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.exceptions import InvalidValue, MalformedError
from pydantic import BaseModel
from fastapi import status
from server.config import CONFIG


class AuthUserInfo(BaseModel):
    email: str
    email_verified: bool
    name: str
    picture: str

    @staticmethod
    def from_dict(info: dict[str, Any]) -> "AuthUserInfo":
        return AuthUserInfo(
            email=info["email"],
            email_verified=info["email_verified"],
            name=info["name"],
            picture=info["picture"],
        )


class AuthenticationClient:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def verify_access_token(self) -> Any:
        token_info_url = "https://oauth2.googleapis.com/tokeninfo"
        params = {"access_token": self.access_token}

        response = requests.get(token_info_url, params=params)
        if response.status_code == 200:
            # Token is valid
            token_info = response.json()
            return token_info  # Contains user_id, scopes, etc.
        else:
            raise HTTPException(status_code=401, detail="Code invalid or expired")

    def get_user_info(self) -> AuthUserInfo:
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(userinfo_url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            return AuthUserInfo.from_dict(user_info)
        else:
            raise HTTPException(status_code=401, detail="Error getting user info from access token")

    def get_email(self) -> str:
        return self.get_user_info().email


class InvalidAuthTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token invalid")
