from typing import Any
from google.oauth2 import id_token
from google.auth.transport import requests
from server.config import CONFIG


def authenticate_with_google(idToken: str) -> Any:
    # Specify the CLIENT_ID of the app that accesses the backend:
    idInfo = id_token.verify_oauth2_token(
        idToken, requests.Request(), CONFIG.google_auth_mobile_client_id
    )

    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    # Reject unless the account is both on an allowed Workspace domain and
    # has a verified email - previously an `and`, which let an unverified
    # email from *any* domain skip the domain check entirely.
    if (
        idInfo["hd"] not in CONFIG.allowed_gmails_domains
        or not idInfo["email_verified"]
    ):
        raise ValueError("Wrong domain name.")

    # ID token is valid. Get the user's Google Account ID from the decoded token.
    return idInfo
