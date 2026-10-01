from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status

from server.utils.google_auth_utils import authenticate_with_google


class InvalidGoogleIdToken(HTTPException):
    def __init__(self, detail: str = "Invalid idToken") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def google_id_token_authenticate(idToken: Annotated[str, Header()]) -> Any:
    """Authenticate a mobile client via the Google ID token sent in the
    idToken header (used by the mobile authentication routes)."""
    try:
        return authenticate_with_google(idToken)
    except ValueError as exc:
        raise InvalidGoogleIdToken(str(exc)) from exc


def google_authorization_authenticate(authorization: str = Header(None)) -> Any:
    """Authenticate a mobile client via the Google ID token sent in the
    Authorization header (used by the forum routes)."""
    try:
        return authenticate_with_google(authorization)
    except ValueError as exc:
        raise InvalidGoogleIdToken(str(exc)) from exc


GoogleIdTokenDep = Annotated[Any, Depends(google_id_token_authenticate)]
GoogleAuthorizationDep = Annotated[Any, Depends(google_authorization_authenticate)]
