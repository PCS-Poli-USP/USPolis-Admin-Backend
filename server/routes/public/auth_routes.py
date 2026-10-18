from fastapi import APIRouter, Body, HTTPException, Request, Response, status

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server.config import CONFIG
from server.deps.authenticate import AuthenticationClient
from server.services.auth.authentication_client import AuthProviderUnavailable
from server.deps.session_dep import SessionDep
from server.middlewares import get_client_ip
from server.models.database.user_session_db_model import UserSession
from server.repositories.user_repository import UserRepository
from server.repositories.user_session_repository import (
    SESSION_MAX_AGE_DAYS,
    IssuedSession,
    UserSessionRepository,
)
from server.services.security.csrf import (
    UntrustedOriginForCookie,
    is_trusted_cookie_request,
)
from server.utils.must_be_int import must_be_int

embed = Body(..., embed=True)

router = APIRouter(prefix="/auth", tags=["Auth"])


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str


# The browser keeps the cookie up to the absolute cap; the server decides
# whether the session is still valid (expires_at, slid on every use).
SESSION_COOKIE_AGE = 60 * 60 * 24 * SESSION_MAX_AGE_DAYS


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="none" if CONFIG.development else "lax",
        max_age=SESSION_COOKIE_AGE,
        path="/",
    )


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
    ip_address = get_client_ip(request)
    user_id = must_be_int(user.id)

    issued: IssuedSession | None = None
    session_token = request.cookies.get("session")
    if session_token:
        current = UserSessionRepository.get_valid_session_for_renewal(
            token=session_token, user_id=user_id, session=session
        )
        if current is not None:
            UserSessionRepository.extend_session(user_session=current, session=session)
            # A real login always gets a new token (no session fixation).
            issued = IssuedSession(
                user_session=current,
                token=UserSessionRepository.rotate_token(
                    user_session=current, session=session
                ),
            )

    if issued is None and user_agent is not None and ip_address is not None:
        issued = UserSessionRepository.start_or_renew_session(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            session=session,
        )

    if issued is not None:
        _set_session_cookie(response, issued.token)
    else:
        response.delete_cookie("session")

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
    except AuthProviderUnavailable:
        # Google is down, not the token: keep the user's session.
        raise
    except HTTPException:
        session_token = request.cookies.get("session")
        if session_token:
            stale = UserSessionRepository.get_by_token_opt(
                token=session_token, session=session
            )
            if stale is not None:
                session.delete(stale)
                session.commit()

        raise InvalidRefreshToken()

    session_token = request.cookies.get("session")
    user_session: UserSession | None = None
    # The cookie value to (re)send: the browser's own token when its session
    # is found, a new one when a session is adopted or created below.
    cookie_token: str | None = None
    if session_token:
        user_session = UserSessionRepository.get_by_token_opt(
            token=session_token, session=session
        )
        if user_session is not None:
            cookie_token = session_token

    if user_session:
        UserSessionRepository.extend_session(user_session=user_session, session=session)
        session.commit()

    if not user_session:
        user_info = AuthenticationClient.get_user_info(new_access_token)
        user = UserRepository.get_by_email(email=user_info.email, session=session)
        user_agent = request.headers.get("user-agent")
        ip_address = get_client_ip(request)

        if user_agent is not None:
            user_session = UserSessionRepository.get_session(
                user_id=must_be_int(user.id),
                user_agent=user_agent,
                session=session,
            )
            if user_session is not None:
                # Its current token is unknown (only the hash is stored).
                cookie_token = UserSessionRepository.rotate_token(
                    user_session=user_session, session=session
                )

        if not user_session and user_agent is not None and ip_address is not None:
            user_session, cookie_token = UserSessionRepository.create_session(
                user_id=must_be_int(user.id),
                user_agent=user_agent,
                ip_address=ip_address,
                session=session,
            )
        session.commit()

    if cookie_token is not None:
        _set_session_cookie(response, cookie_token)
    else:
        response.delete_cookie("session")

    return RefreshTokenResponse(access_token=new_access_token)


@router.post("/logout")
def logout(db: SessionDep, request: Request, response: Response) -> JSONResponse:
    session_token = request.cookies.get("session")
    if session_token:
        # Otherwise any page could log users out with a cross-site POST.
        if not is_trusted_cookie_request(request):
            raise UntrustedOriginForCookie()
        user_session = UserSessionRepository.get_by_token_opt(
            token=session_token, session=db
        )
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
