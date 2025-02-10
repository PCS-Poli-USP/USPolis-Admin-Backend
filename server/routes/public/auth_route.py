from fastapi import APIRouter, Body, HTTPException, status

from pydantic import BaseModel

from server.deps.authenticate import AuthenticationClient

embed = Body(..., embed=True)

router = APIRouter(prefix="/auth", tags=["Auth", "Public"])


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str


@router.get("/get-tokens")
async def get_tokens(auth_code: str) -> AuthResponse:
    access_token, refresh_token = AuthenticationClient.exchange_auth_code_for_tokens(
        auth_code
    )
    if access_token is None or refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="null token received"
        )
    return AuthResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/refresh-token")
async def refresh_token(refresh_token: str) -> RefreshTokenResponse:
    new_access_token = AuthenticationClient.refresh_access_token(
        refresh_token=refresh_token
    )
    return RefreshTokenResponse(access_token=new_access_token)
