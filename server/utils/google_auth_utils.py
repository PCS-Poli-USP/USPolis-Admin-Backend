import os
from typing import Any
from google.oauth2 import id_token
from google.auth.transport import requests


def authenticate_with_google(idToken: str) -> Any:
    # Specify the CLIENT_ID of the app that accesses the backend:
    idInfo = id_token.verify_oauth2_token(
        idToken, requests.Request(), os.getenv("G_AUTH_CLIENT_ID")
    )

    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    print(idInfo)
    # If the request specified a Google Workspace domain
    if idInfo["hd"] != os.getenv("G_AUTH_DOMAIN_NAME") and idInfo["email_verified"]:
        raise ValueError("Wrong domain name.")

    # ID token is valid. Get the user's Google Account ID from the decoded token.
    return idInfo
