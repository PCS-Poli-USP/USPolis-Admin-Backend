from fastapi import APIRouter, Body, HTTPException, Request, Response, status

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server.config import CONFIG
from server.deps.authenticate import AuthenticationClient
from server.deps.session_dep import SessionDep
from server.models.database.user_session_db_model import UserSession
from server.repositories.user_repository import UserRepository
from server.repositories.user_session_repository import UserSessionRepository
from server.utils.must_be_int import must_be_int

embed = Body(..., embed=True)

router = APIRouter(prefix="/auth", tags=["Auth"])


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str


SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 dias


@router.get("/get-tokens")
def get_tokens(
    auth_code: str, request: Request, response: Response, session: SessionDep
) -> AuthResponse:
    access_token, refresh_token = AuthenticationClient.exchange_auth_code_for_tokens(
        auth_code
    )
    if access_token is None or refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="null token received"
        )
    user_info = AuthenticationClient.get_user_info(access_token)
    user = UserRepository.get_from_auth(user_info=user_info, session=session)
    user_agent = request.headers.get("user-agent")
    ip_address = None
    if request.client:
        ip_address = request.client.host
    user_session = UserSessionRepository.create_session(
        user_id=must_be_int(user.id),
        user_agent=user_agent,
        ip_address=ip_address,
        session=session,
    )

    response.set_cookie(
        key="session",
        value=user_session.id,
        httponly=True,
        secure=True,
        samesite="none" if CONFIG.development else "lax",
        max_age=SESSION_COOKIE_AGE,
        path="/",
    )
    session.commit()
    return AuthResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/refresh-token")
def refresh_token(
    refresh_token: str, response: Response, request: Request, session: SessionDep
) -> RefreshTokenResponse:
    try:
        new_access_token = AuthenticationClient.refresh_access_token(
            refresh_token=refresh_token
        )
    except HTTPException:
        session_id = request.cookies.get("session")
        user_session: UserSession | None = None
        if session_id:
            user_session = UserSessionRepository.get_session_by_id(
                id=session_id, session=session
            )
            session.delete(user_session)
            session.commit()

        raise InvalidRefreshToken()

    session_id = request.cookies.get("session")
    user_session = None
    if session_id:
        user_session = UserSessionRepository.get_session_opt(
            id=session_id, session=session
        )

    if user_session:
        UserSessionRepository.extend_session(user_session=user_session, session=session)
        session.commit()

    if not user_session:
        user_info = AuthenticationClient.get_user_info(new_access_token)
        user = UserRepository.get_by_email(email=user_info.email, session=session)
        user_agent = request.headers.get("user-agent")
        ip_address = None
        if request.client:
            ip_address = request.client.host

        user_session = UserSessionRepository.get_session(
            user_id=must_be_int(user.id),
            user_agent=user_agent,
            ip_address=ip_address,
            session=session,
        )
        if not user_session:
            user_session = UserSessionRepository.create_session(
                user_id=must_be_int(user.id),
                user_agent=user_agent,
                ip_address=ip_address,
                session=session,
            )
        session.commit()

    response.set_cookie(
        key="session",
        value=user_session.id,
        httponly=True,
        secure=True,
        samesite="none" if CONFIG.development else "lax",
        max_age=SESSION_COOKIE_AGE,
        path="/",
    )
    return RefreshTokenResponse(access_token=new_access_token)


@router.post("/logout")
def logout(db: SessionDep, request: Request, response: Response) -> JSONResponse:
    session_id = request.cookies.get("session")
    if session_id:
        user_session = UserSessionRepository.get_session_opt(id=session_id, session=db)
        if user_session:
            db.delete(user_session)
            db.commit()

    response.delete_cookie("session")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Usuário deslogado com sucesso!"},
    )


class InvalidRefreshToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
