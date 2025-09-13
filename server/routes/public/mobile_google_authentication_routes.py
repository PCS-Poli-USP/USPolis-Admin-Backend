from typing import Annotated
from fastapi import APIRouter, Header

from google.oauth2 import id_token
from google.auth.transport import requests

from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.repositories.mobile_user_repository import MobileUserRepository
from server.models.http.responses.mobile_auth_user_response_models import (
    AuthenticationResponse,
)
from server.utils.google_auth_utils import authenticate_with_google
from server.config import CONFIG

router = APIRouter(prefix="/mobile/authentication", tags=["Mobile", "Authenticate"])


@router.post("")
async def authenticate_user(
    idToken: Annotated[str | None, Header()], session: SessionDep
) -> AuthenticationResponse:
    """Authenticates user with Google: if it is in our DB return user info"""
    if idToken is None:
        raise ValueError("Invalid idToken")
    idInfo = authenticate_with_google(idToken)

    sub = idInfo["sub"]

    mobileUser = MobileUserRepository.get_user_by_sub(sub=sub, session=session)
    return AuthenticationResponse.from_model_user(modelUser=mobileUser)


@router.post("/new-user")
async def create_new_user(
    idToken: Annotated[str | None, Header()], session: SessionDep
) -> AuthenticationResponse:
    """Validates the token and creates a new user and store its information in the DB (received from the Google API)"""
    userInfo = id_token.verify_oauth2_token(
        idToken, requests.Request(), CONFIG.google_auth_mobile_client_id
    )

    newUser = MobileUser(
        sub=userInfo["sub"],  # The unique ID of the user's Google Account
        given_name=userInfo["given_name"],
        family_name=userInfo["family_name"],
        email=userInfo["email"],
        picture_url=userInfo["picture"],
    )

    new_user = MobileUserRepository.create(new_user=newUser, session=session)
    return AuthenticationResponse.from_model_user(new_user)
