import secrets

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.config import CONFIG
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingRepository
from server.repositories.user_repository import UserRepository
from server.repositories.user_session_repository import (
    UserSessionNotFound,
    UserSessionRepository,
)
from server.services.auth.auth_user_info import AuthUserInfo
from server.services.auth.authentication_client import (
    AuthenticationClient,
)
from server.deps.session_dep import SessionDep

security = HTTPBearer(auto_error=False)


# -- token authentications :


def health_token_authenticate(x_api_key: str = Header(...)) -> None:
    if not secrets.compare_digest(x_api_key, CONFIG.health_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


def google_token_authenticate(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> AuthUserInfo:
    if credentials is None or not credentials.credentials:
        raise InvalidToken()
    access_token = credentials.credentials
    return AuthenticationClient.get_user_info(access_token)


def public_token_authenticate(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> None:
    """Authenticate public routes, but do not raise if no credentials are provided."""
    if credentials is not None and credentials.credentials:
        access_token = credentials.credentials
        try:
            user_info = AuthenticationClient.get_user_info(access_token)
            request.state.user_info = user_info
        except Exception:
            pass


def token_authenticate(
    request: Request,
    user_info: Annotated[AuthUserInfo, Depends(google_token_authenticate)],
    session: SessionDep,
) -> User:
    user = UserRepository.get_from_auth(user_info=user_info, session=session)
    if not user.picture_url:
        user.picture_url = user_info.picture
        session.add(user)
        session.commit()

    request.state.current_user = user
    request.state.user_info = user_info
    return user


def restricted_token_authenticate(
    user: Annotated[User, Depends(token_authenticate)],
) -> User:
    if user.is_admin:
        return user
    if not user.groups:
        raise RestrictedAccessRequired()
    return user


def admin_token_authenticate(
    user: Annotated[User, Depends(token_authenticate)],
) -> None:
    if not user.is_admin:
        raise AdminAccessRequired()


# -- cookie authentications :
def public_authenticate_from_cookie(request: Request, session: SessionDep) -> None:
    session_id = request.cookies.get("session")
    if session_id:
        try:
            user_session = UserSessionRepository.get_session_by_id(
                id=session_id, session=session
            )
            request.state.current_user = user_session.user
        except UserSessionNotFound:
            pass


def authenticate_from_cookie(request: Request, session: SessionDep) -> User:
    session_id = request.cookies.get("session")
    if not session_id:
        raise InvalidSessionCookie()
    try:
        user_session = UserSessionRepository.get_session_by_id(
            id=session_id, session=session
        )
    except UserSessionNotFound:
        raise InvalidSessionCookie()
    return user_session.user


def restricted_authenticate_from_cookie(
    user: Annotated[User, Depends(authenticate_from_cookie)],
) -> User:
    if user.is_admin:
        return user
    if not user.groups:
        raise RestrictedAccessRequired()
    return user


def admin_authenticate_from_cookie(
    user: Annotated[User, Depends(authenticate_from_cookie)],
) -> None:
    if not user.is_admin:
        raise AdminAccessRequired()


# -- general authentications :
def public_authenticate(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionDep,
) -> None:
    """Authenticate the user using either a token or a session cookie, but do not raise if no credentials are provided."""
    try:
        user_info = google_token_authenticate(
            credentials=credentials,
        )
        token_authenticate(request=request, user_info=user_info, session=session)
    except HTTPException:
        public_authenticate_from_cookie(request=request, session=session)


def authenticate(
    request: Request,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """Authenticate the user using either a token or a session cookie."""
    try:
        user_info = google_token_authenticate(
            credentials=credentials,
        )
        return token_authenticate(request=request, user_info=user_info, session=session)
    except HTTPException:
        return authenticate_from_cookie(request=request, session=session)


def restricted_authenticate(
    request: Request,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """Authenticate the user using either a token or a session cookie, and check if they have restricted access."""
    try:
        user_info = google_token_authenticate(
            credentials=credentials,
        )
        return restricted_token_authenticate(
            token_authenticate(request=request, user_info=user_info, session=session)
        )
    except HTTPException:
        return restricted_authenticate_from_cookie(
            authenticate_from_cookie(request=request, session=session)
        )


def admin_authenticate(
    request: Request,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> None:
    """Authenticate the user using either a token or a session cookie, and check if they are an admin."""
    try:
        user_info = google_token_authenticate(
            credentials=credentials,
        )
        admin_token_authenticate(
            token_authenticate(request=request, user_info=user_info, session=session)
        )
    except HTTPException:
        admin_authenticate_from_cookie(
            authenticate_from_cookie(request=request, session=session)
        )


# -- permission authentications :


def building_authenticate(
    user: Annotated[User, Depends(authenticate)],
    session: SessionDep,
    building_id: Annotated[int, Header()],
) -> Building:
    building = BuildingRepository.get_by_id(id=building_id, session=session)
    if user.is_admin:
        return building
    if user.buildings is None or building not in user.buildings:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Usuário não tem permissão para acessar o prédio {building.name}",
        )
    return building


class InvalidToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
        self.headers = {"WWW-Authenticate": "Bearer"}


class InvalidSessionCookie(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cookie de sessão inválido",
        )


class AdminAccessRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deve ser administrador",
        )


class RestrictedAccessRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deve ter acesso restrito a algum grupo",
        )


# exports:
GoogleAuthenticate = Annotated[AuthUserInfo, Depends(google_token_authenticate)]
UserDep = Annotated[User, Depends(authenticate)]
BuildingDep = Annotated[Building, Depends(building_authenticate)]
