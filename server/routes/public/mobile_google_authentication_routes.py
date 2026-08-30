from fastapi import APIRouter, Depends

from server.deps.google_auth_dep import GoogleIdTokenDep, google_id_token_authenticate
from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.repositories.mobile_user_repository import MobileUserRepository
from server.models.http.responses.mobile_auth_user_response_models import (
    AuthenticationResponse,
)

router = APIRouter(
    prefix="/mobile/authentication",
    tags=["Mobile", "Authenticate"],
    dependencies=[Depends(google_id_token_authenticate)],
)


@router.post("")
async def authenticate_user(
    idInfo: GoogleIdTokenDep, session: SessionDep
) -> AuthenticationResponse:
    """Authenticates user with Google: if it is in our DB return user info"""
    sub = idInfo["sub"]

    mobileUser = MobileUserRepository.get_user_by_sub_or_none(sub=sub, session=session)
    return AuthenticationResponse.from_model_user(modelUser=mobileUser)


@router.post("/new-user")
async def create_new_user(
    idInfo: GoogleIdTokenDep, session: SessionDep
) -> AuthenticationResponse:
    """Validates the token and creates a new user and store its information in the DB (received from the Google API)"""
    newUser = MobileUser(
        sub=idInfo["sub"],  # The unique ID of the user's Google Account
        given_name=idInfo["given_name"],
        family_name=idInfo["family_name"],
        email=idInfo["email"],
        picture_url=idInfo["picture"],
    )

    new_user = MobileUserRepository.create(new_user=newUser, session=session)
    return AuthenticationResponse.from_model_user(new_user)
