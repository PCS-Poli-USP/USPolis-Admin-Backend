import os
from typing import Annotated
from fastapi import APIRouter, Header

from google.oauth2 import id_token
from google.auth.transport import requests

from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.repositories.mobile_user_repository import MobileUserRepository
from server.routes.public.dtos.mobile_auth_user_response import AuthenticationResponse

router = APIRouter(prefix="/mobile/authentication", tags=["Mobile","Authenticate"])

@router.post("")
async def authenticate_user(idToken: Annotated[str | None, Header()], session: SessionDep):
    """Authenticates user with Google: if it is in our DB return user info"""
    # Specify the CLIENT_ID of the app that accesses the backend:
    idInfo = id_token.verify_oauth2_token(idToken, requests.Request(), os.environ["G_AUTH_CLIENT_ID"])
    print(idInfo)
    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    # If the request specified a Google Workspace domain
    if idInfo['hd'] != os.environ["G_AUTH_DOMAIN_NAME"] and idInfo['email_verified']:
        raise ValueError('Wrong domain name.')

    # ID token is valid. Get the user's Google Account ID from the decoded token.
    
    sub = idInfo["sub"]
    print("sub found: ",sub)

    mobileUser = MobileUserRepository.get_user_by_sub(sub=sub, session=session)
    return AuthenticationResponse.from_model_user(modelUser=mobileUser)

@router.post("/new-user")
async def create_new_user(idToken: Annotated[str | None, Header()], session: SessionDep):
    """Validates the token and creates a new user and store its information in the DB (received from the Google API)"""
    userInfo= id_token.verify_oauth2_token(idToken, requests.Request(), os.environ["G_AUTH_CLIENT_ID"])

    newUser = MobileUser(
        sub = userInfo["sub"], # The unique ID of the user's Google Account
        given_name = userInfo["given_name"],
        family_name = userInfo["family_name"],
        email = userInfo["email"],
        picture_url = userInfo["picture"]
    )

    new_user = MobileUserRepository.create(new_user=newUser, session=session)
    return AuthenticationResponse.from_auth_user(new_user)
