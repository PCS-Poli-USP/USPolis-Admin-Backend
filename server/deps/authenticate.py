from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.config import CONFIG
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.repositories.building_repository import BuildingRepository
from server.repositories.user_repository import UserRepository
from server.services.auth.auth_user_info import AuthUserInfo
from server.services.auth.authentication_client import (
    AuthenticationClient,
)
from server.models.http.requests.user_request_models import UserRegister
from sqlalchemy.exc import NoResultFound

security = HTTPBearer(auto_error=False)


def google_authenticate(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> AuthUserInfo:
    if credentials is None or not credentials.credentials:
        raise InvalidToken()
    access_token = credentials.credentials
    return AuthenticationClient.get_user_info(access_token)


def authenticate(
    request: Request,
    user_info: Annotated[AuthUserInfo, Depends(google_authenticate)],
    session: SessionDep,
) -> User:
    try:
        user: User = UserRepository.get_by_email(email=user_info.email, session=session)
    except NoResultFound:
        if user_info.domain != CONFIG.google_auth_domain_name:
            raise InvalidEmailDomain()

        user = UserRepository.create(
            input=UserRegister(
                email=user_info.email,
                name=user_info.name,
                group_ids=[],
                is_admin=False,
            ),
            creator=None,
            session=session,
        )
        session.commit()
        session.refresh(user)
    request.state.current_user = user
    request.state.user_info = user_info
    return user


def restricted_authenticate(
    user: Annotated[User, Depends(authenticate)],
) -> User:
    if user.is_admin:
        return user
    if not user.groups:
        raise RestrictedAccessRequired()
    return user


def admin_authenticate(user: Annotated[User, Depends(authenticate)]) -> None:
    if not user.is_admin:
        raise AdminAccessRequired()


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


class InvalidEmailDomain(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Domínio inválido, deve-se usar domínio USP!",
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
GoogleAuthenticate = Annotated[AuthUserInfo, Depends(google_authenticate)]
UserDep = Annotated[User, Depends(authenticate)]
BuildingDep = Annotated[Building, Depends(building_authenticate)]
