from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status

from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.repositories.mobile_user_repository import MobileUserRepository
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


def mobile_user_authenticate(
    id_info: GoogleAuthorizationDep, session: SessionDep
) -> MobileUser:
    """The app user of the Google token in the Authorization header: whoever
    writes through the app (posts, replies, likes, reports, comments) is taken
    from the token, never from the body."""
    user = MobileUserRepository.get_user_by_sub_or_none(
        sub=id_info["sub"], session=session
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta Google ainda não tem usuário no app",
        )
    return user


MobileUserDep = Annotated[MobileUser, Depends(mobile_user_authenticate)]


def check_acting_as(user: MobileUser, user_id: int | None) -> None:
    """The `user_id` a request body carries must be the token's user (the app
    still sends it): nobody acts as another user."""
    if user_id is not None and user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O usuário da requisição não é o usuário autenticado",
        )
