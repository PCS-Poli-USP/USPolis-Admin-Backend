import os
from typing import Annotated
from fastapi import APIRouter, Header

from google.oauth2 import id_token
from google.auth.transport import requests

from server.deps.session_dep import SessionDep

router = APIRouter(prefix="/mobile/authentication", tags=["Mobile","Authenticate"])

@router.post("")
async def authenticate_user(idToken: Annotated[str | None, Header()], session: SessionDep):
    """Authenticates user: if it is not in our DB save it, else retrive data"""
    # Specify the CLIENT_ID of the app that accesses the backend:
    idinfo = id_token.verify_oauth2_token(idToken, requests.Request(), os.environ["G_AUTH_CLIENT_ID"])
    print(idinfo)
    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    # If the request specified a Google Workspace domain
    if idinfo['hd'] != os.environ["G_AUTH_DOMAIN_NAME"]:
        raise ValueError('Wrong domain name.')

    # ID token is valid. Get the user's Google Account ID from the decoded token.
    userEmail = idinfo['email']
    userName = idinfo['name']
    userPicture = idinfo['picture']
    print(userEmail, userName, userPicture)
