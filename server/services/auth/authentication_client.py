from typing import Annotated, Any, Self
from fastapi import APIRouter, Header
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel


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
    def __init__(self, token: str):
        self.token = token

    def get_user_info(self) -> AuthUserInfo:
        userInfo = id_token.verify_oauth2_token(
            self.token,
            requests.Request(),
            "903358108153-kj9u7e4liu19cm73lr6hlhi876smdscj.apps.googleusercontent.com",
        )
        return AuthUserInfo.from_dict(userInfo)

    def get_email(self) -> str:
        return self.get_user_info().email
    
