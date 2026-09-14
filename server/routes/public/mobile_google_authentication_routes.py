from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from google.oauth2 import id_token
from google.auth.transport import requests

from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.repositories.mobile_user_repository import MobileUserRepository
from server.models.http.responses.mobile_auth_user_response_models import (
    AuthenticationResponse,
)
from server.routes.public.auth_routes import AuthResponse
from server.utils.google_auth_utils import authenticate_with_google
from server.config import CONFIG
from server.repositories.user_session_repository import UserSessionRepository
from server.models.database.user_session_db_model import UserSession

from server.repositories.user_repository import UserRepository
from server.services.auth.auth_user_info import AuthUserInfo
from server.services.auth.authentication_client import AuthenticationClient
from server.utils.must_be_int import must_be_int

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

@router.post("/login")
def login(
    request: Request,
    response: Response,
    session: SessionDep,
    idToken: Annotated[str | None, Header()] = None,
    serverAuthCode: Annotated[str | None, Header()] = None,
) -> AuthResponse:

    if idToken is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="idToken não informado",
        )

    if serverAuthCode is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="serverAuthCode não informado",
        )

    # 1. Valida o ID Token
    try:
        user_info_dict = id_token.verify_oauth2_token(
            idToken,
            requests.Request(),
            CONFIG.google_auth_client_id,
        )
    except Exception as e:
        print("ERRO AO VALIDAR ID TOKEN:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google inválido",
        )

    # 2. Verifica email institucional
    email = user_info_dict.get("email")
    email_verified = user_info_dict.get("email_verified", False)
    domain = user_info_dict.get("hd")

    if (
        not email
        or not email_verified
        or (
            domain not in CONFIG.allowed_gmails_domains
            and email not in CONFIG.allowed_gmails
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="É necessário usar um email institucional para acessar o sistema",
        )

    # 3. Converte os dados do Google para AuthUserInfo
    user_info = AuthUserInfo.from_dict(dict(user_info_dict))

    # 4. Busca/cria o usuário normal do USPolis
    user = UserRepository.get_from_auth(
        user_info=user_info,
        session=session,
    )

    # 5. Troca o serverAuthCode pelos tokens do Google
    access_token, refresh_token = (
        AuthenticationClient.exchange_server_auth_code_for_tokens(
            server_auth_code=serverAuthCode
        )
    )

    print("ACCESS TOKEN EXISTE:", access_token is not None)
    print("REFRESH TOKEN EXISTE:", refresh_token is not None)

    if access_token is None or refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível obter os tokens do Google",
        )

    # 6. Cria/atualiza a sessão do USPolis
    user_agent = request.headers.get("user-agent")

    ip_address = None
    if request.client:
        ip_address = request.client.host

    user_session: UserSession | None = None

    if user_agent is not None and ip_address is not None:
        user_session = UserSessionRepository.get_session(
            user_id=must_be_int(user.id),
            user_agent=user_agent,
            ip_address=ip_address,
            session=session,
        )

    if user_session:
        UserSessionRepository.extend_session(
            user_session=user_session,
            session=session,
        )

    if (
        not user_session
        and user_agent is not None
        and ip_address is not None
    ):
        user_session = UserSessionRepository.create_session(
            user_id=must_be_int(user.id),
            user_agent=user_agent,
            ip_address=ip_address,
            session=session,
        )

    if user_session is not None:
        response.set_cookie(
            key="session",
            value=user_session.id,
            httponly=True,
            secure=True,
            samesite="none" if CONFIG.development else "lax",
            max_age=60 * 60 * 24 * 30,
            path="/",
        )

    if user_session is None:
        response.delete_cookie("session")

    session.commit()

    # 7. Retorna os tokens
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )