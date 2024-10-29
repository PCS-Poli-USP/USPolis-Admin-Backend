import requests

from fastapi import APIRouter, Body, HTTPException
from typing import Any, Tuple

from pydantic import BaseModel

from server.config import CONFIG

embed = Body(..., embed=True)

router = APIRouter(prefix="/auth", tags=["Auth", "Public"])


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str


@router.get("/get-tokens")
async def get_tokens(auth_code: str) -> AuthResponse:
    access_token, refresh_token = exchange_auth_code_for_tokens(auth_code)
    if access_token is None or refresh_token is None:
        raise HTTPException(status_code=401, detail="null token received")
    return AuthResponse(access_token=access_token, refresh_token=refresh_token)

@router.get("/refresh-token")
async def refresh_token(refresh_token: str) -> RefreshTokenResponse:
    new_access_token = refresh_access_token(refresh_token=refresh_token)
    return RefreshTokenResponse(access_token=new_access_token)

def exchange_auth_code_for_tokens(auth_code: str) -> Tuple[str, str | None]:
    token_url = "https://oauth2.googleapis.com/token"

    redirect_uri = "http://localhost:3000/auth-callback"

    data = {
        "code": auth_code,
        "client_id": CONFIG.google_auth_client_id,
        "client_secret": CONFIG.google_auth_client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    # Make the request to exchange the code for tokens
    response = requests.post(token_url, data=data)
    response_data = response.json()

    # Check for successful response
    if "access_token" in response_data:
        access_token = response_data["access_token"]
        refresh_token = response_data.get("refresh_token")
        return access_token, refresh_token
    else:
        print("Error exchanging auth code for tokens:", response_data)
        raise HTTPException(status_code=401, detail=response_data)


def refresh_access_token(refresh_token: str) -> Any:
    # Google OAuth 2.0 token endpoint
    token_url = "https://oauth2.googleapis.com/token"
    
    # Your client credentials
    client_id = CONFIG.google_auth_client_id
    client_secret = CONFIG.google_auth_client_secret
    
    # Prepare the data for the request
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    # Make the request to refresh the access token
    response = requests.post(token_url, data=data)
    response_data = response.json()
    
    # Check for successful response
    if "access_token" in response_data:
        access_token = response_data["access_token"]
        return access_token
    else:
        # Handle errors
        raise HTTPException(status_code=401, detail="Error refreshing token")