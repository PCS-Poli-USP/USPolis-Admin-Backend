import hashlib
import json
import requests
from typing import Any
from fastapi import HTTPException
from fastapi import status
from redis.exceptions import RedisError
from server.config import CONFIG
from server.logger import logger
from server.services.auth.auth_user_info import AuthUserInfo
from server.services.redis_client import get_sync_redis

# Every call to Google runs inside a sync route/dependency, i.e. on one of
# the worker's threadpool threads: without a timeout a slow Google would pin
# those threads indefinitely and stall the whole worker.
GOOGLE_REQUEST_TIMEOUT_SECONDS = 5


class AuthProviderUnavailable(HTTPException):
    """Google did not answer in time (or at all). Distinct from a 401 so
    callers never treat an outage as an invalid credential."""

    def __init__(self) -> None:
        super().__init__(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Serviço de autenticação do Google indisponível, tente novamente",
        )


# Every public request carrying a Bearer token used to cost one call to
# Google, so `Bearer garbage` turned the API into a request amplifier. The
# userinfo answer is cached per token (keyed by its hash, never the token
# itself): 5 min for valid ones (Google access tokens last 1 h, so a revoked
# token keeps working for at most that long) and 1 min for rejected ones.
USER_INFO_CACHE_PREFIX = "auth:google:userinfo:"
USER_INFO_CACHE_SECONDS = 300
INVALID_TOKEN_CACHE_SECONDS = 60
_INVALID_TOKEN_MARKER = b"invalid"
# Google's answers to a bad token. Anything else (5xx, 429) may be Google's
# own trouble and must not lock a valid token out for a minute.
_GOOGLE_REJECTED_TOKEN_STATUSES = (400, 401)


def _user_info_cache_key(access_token: str) -> str:
    return USER_INFO_CACHE_PREFIX + hashlib.sha256(access_token.encode()).hexdigest()


def _cache_get(key: str) -> bytes | None:
    """Fails open: no Redis (or a Redis error) just means a cache miss."""
    redis = None if CONFIG.testing else get_sync_redis()
    if redis is None:
        return None
    try:
        value = redis.get(key)
    except (RedisError, OSError) as e:
        logger.error(f"Google userinfo cache read failed: {e}")
        return None
    return value if isinstance(value, bytes) else None


def _cache_set(key: str, value: bytes, ttl_seconds: int) -> None:
    redis = None if CONFIG.testing else get_sync_redis()
    if redis is None:
        return
    try:
        redis.set(key, value, ex=ttl_seconds)
    except (RedisError, OSError) as e:
        logger.error(f"Google userinfo cache write failed: {e}")


def _google_get(url: str, **kwargs: Any) -> requests.Response:
    try:
        return requests.get(url, timeout=GOOGLE_REQUEST_TIMEOUT_SECONDS, **kwargs)
    except requests.RequestException:
        raise AuthProviderUnavailable()


def _google_post(url: str, **kwargs: Any) -> requests.Response:
    try:
        return requests.post(url, timeout=GOOGLE_REQUEST_TIMEOUT_SECONDS, **kwargs)
    except requests.RequestException:
        raise AuthProviderUnavailable()


class AuthenticationClient:
    token_url = "https://oauth2.googleapis.com/token"
    token_info_url = "https://oauth2.googleapis.com/tokeninfo"
    redirect_uri = CONFIG.google_auth_redirect_uri

    @staticmethod
    def verify_access_token(access_token: str) -> Any:
        params = {"access_token": access_token}

        response = _google_get(AuthenticationClient.token_info_url, params=params)
        if response.status_code == 200:
            token_info = response.json()
            return token_info
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code invalid or expired",
            )

    @staticmethod
    def get_user_info(access_token: str) -> AuthUserInfo:
        user_info = AuthenticationClient._fetch_user_info(access_token)
        auth_info = AuthUserInfo.from_dict(user_info)
        # Checked on every call, cached or not: an allowlist change applies
        # right away.
        if (
            auth_info.domain not in CONFIG.allowed_gmails_domains
            and auth_info.email not in CONFIG.allowed_gmails
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="É necessário usar um email institucional para acessar o sistema",
            )
        return auth_info

    @staticmethod
    def _fetch_user_info(access_token: str) -> Any:
        """Google's userinfo payload for the token, from the cache when
        possible (see USER_INFO_CACHE_SECONDS)."""
        invalid = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error getting user info from access token",
        )
        cache_key = _user_info_cache_key(access_token)
        cached = _cache_get(cache_key)
        if cached == _INVALID_TOKEN_MARKER:
            raise invalid
        if cached is not None:
            try:
                return json.loads(cached)
            except ValueError:
                pass  # corrupt entry: ask Google again and overwrite it

        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = _google_get(userinfo_url, headers=headers)
        if response.status_code != 200:
            if response.status_code in _GOOGLE_REJECTED_TOKEN_STATUSES:
                _cache_set(
                    cache_key, _INVALID_TOKEN_MARKER, INVALID_TOKEN_CACHE_SECONDS
                )
            raise invalid

        user_info = response.json()
        _cache_set(cache_key, json.dumps(user_info).encode(), USER_INFO_CACHE_SECONDS)
        return user_info

    @staticmethod
    def exchange_auth_code_for_tokens(auth_code: str) -> tuple[str, str | None]:
        data = {
            "code": auth_code,
            "client_id": CONFIG.google_auth_client_id,
            "client_secret": CONFIG.google_auth_client_secret,
            "redirect_uri": AuthenticationClient.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = _google_post(AuthenticationClient.token_url, data=data)
        response_data = response.json()

        if "access_token" in response_data:
            access_token = response_data["access_token"]
            refresh_token = response_data.get("refresh_token")
            return access_token, refresh_token
        else:
            print("Error exchanging auth code for tokens:", response_data)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=response_data
            )

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Any:
        token_url = "https://oauth2.googleapis.com/token"
        client_id = CONFIG.google_auth_client_id
        client_secret = CONFIG.google_auth_client_secret

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = _google_post(token_url, data=data)
        response_data = response.json()

        if "access_token" in response_data:
            access_token = response_data["access_token"]
            return access_token
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error refreshing token",
            )


class InvalidAuthTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token invalid")


class ExpiredAuthTokenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token expired")
