import requests
from typing import Any
from fastapi import HTTPException
from fastapi import status
from server.config import CONFIG
from server.services.auth.auth_user_info import AuthUserInfo


class AuthenticationClient:
    token_url = "https://oauth2.googleapis.com/token"
    token_info_url = "https://oauth2.googleapis.com/tokeninfo"
    redirect_uri = CONFIG.google_auth_redirect_uri

    @staticmethod
    def verify_access_token(access_token: str) -> Any:
        params = {"access_token": access_token}

        response = requests.get(AuthenticationClient.token_info_url, params=params)
        if response.status_code == 200:
            token_info = response.json()
            return token_info
        else:
            raise HTTPException(status_code=401, detail="Code invalid or expired")

    @staticmethod
    def get_user_info(access_token: str) -> AuthUserInfo:
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(userinfo_url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            return AuthUserInfo.from_dict(user_info)
        else:
            raise HTTPException(
                status_code=401, detail="Error getting user info from access token"
            )

    @staticmethod
    def exchange_auth_code_for_tokens(auth_code: str) -> tuple[str, str | None]:

        data = {
            "code": auth_code,
            "client_id": CONFIG.google_auth_client_id,
            "client_secret": CONFIG.google_auth_client_secret,
            "redirect_uri": AuthenticationClient.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(AuthenticationClient.token_url, data=data)
        response_data = response.json()

        if "access_token" in response_data:
            access_token = response_data["access_token"]
            refresh_token = response_data.get("refresh_token")
            return access_token, refresh_token
        else:
            print("Error exchanging auth code for tokens:", response_data)
            raise HTTPException(status_code=401, detail=response_data)

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Any:
        token_url = "https://oauth2.googleapis.com/token"
        client_id = CONFIG.google_auth_client_id
        client_secret = CONFIG.google_auth_client_secret

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(token_url, data=data)
        response_data = response.json()

        if "access_token" in response_data:
            access_token = response_data["access_token"]
            return access_token
        else:
            raise HTTPException(status_code=401, detail="Error refreshing token")


class InvalidAuthTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token invalid")

class ExpiredAuthTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token expired")
