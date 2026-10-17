"""Admin management of partner API clients and keys (see docs/API_KEYS.md).

There is no DELETE: deactivate a client or revoke a key instead, so the
audit trail (who issued/revoked what, when and why) is kept.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Response, status

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.api_key_request_models import (
    ApiClientActiveUpdate,
    ApiClientRegister,
    ApiClientUpdate,
    ApiKeyLinkEmailSend,
    ApiKeyRateLimitsUpdate,
    ApiKeyRegister,
    ApiKeyRevoke,
    ApiKeyUpdate,
    ApiKeyViaLinkRegister,
)
from server.models.http.requests.email_request_models import ApiKeyLinkMail
from server.models.http.responses.api_key_response_models import (
    ApiClientResponse,
    ApiKeyCreatedResponse,
    ApiKeyDeliveryLinkResponse,
    ApiKeyLinkCreatedResponse,
    ApiKeyResponse,
)
from server.repositories.api_client_repository import ApiClientRepository
from server.repositories.api_key_delivery_link_repository import (
    ApiKeyDeliveryLinkRepository,
)
from server.repositories.api_key_repository import ApiKeyRepository
from server.services.email.email_service import EmailService
from server.services.security.api_key_auth import invalidate_api_key_cache
from server.services.security.api_key_link_crypto import delivery_link_url
from server.logger import logger

router = APIRouter(tags=["API Keys"])


@router.get("/api-clients")
def get_api_clients(session: SessionDep) -> list[ApiClientResponse]:
    clients = ApiClientRepository.get_all(session=session)
    return ApiClientResponse.from_api_clients(clients)


@router.post("/api-clients", status_code=status.HTTP_201_CREATED)
def create_api_client(
    input: ApiClientRegister, user: UserDep, session: SessionDep
) -> ApiClientResponse:
    client = ApiClientRepository.create(input=input, user=user, session=session)
    session.commit()
    session.refresh(client)
    return ApiClientResponse.from_api_client(client)


@router.get("/api-clients/{client_id}")
def get_api_client(client_id: int, session: SessionDep) -> ApiClientResponse:
    client = ApiClientRepository.get_by_id(id=client_id, session=session)
    return ApiClientResponse.from_api_client(client)


@router.put("/api-clients/{client_id}")
def update_api_client(
    client_id: int, input: ApiClientUpdate, session: SessionDep
) -> ApiClientResponse:
    client = ApiClientRepository.update(id=client_id, input=input, session=session)
    session.commit()
    session.refresh(client)
    return ApiClientResponse.from_api_client(client)


@router.patch("/api-clients/{client_id}/active")
def set_api_client_active(
    client_id: int, input: ApiClientActiveUpdate, session: SessionDep
) -> ApiClientResponse:
    """Kill switch: deactivating rejects all of the client's keys at once."""
    client = ApiClientRepository.set_active(
        id=client_id, is_active=input.is_active, session=session
    )
    session.commit()
    session.refresh(client)
    invalidate_api_key_cache(key.public_id for key in client.keys)
    return ApiClientResponse.from_api_client(client)


@router.get("/api-clients/{client_id}/keys")
def get_api_client_keys(client_id: int, session: SessionDep) -> list[ApiKeyResponse]:
    ApiClientRepository.get_by_id(id=client_id, session=session)
    keys = ApiKeyRepository.get_all_by_client(client_id=client_id, session=session)
    return ApiKeyResponse.from_api_keys(keys)


@router.post("/api-clients/{client_id}/keys", status_code=status.HTTP_201_CREATED)
def create_api_key(
    client_id: int,
    input: ApiKeyRegister,
    user: UserDep,
    session: SessionDep,
    response: Response,
) -> ApiKeyCreatedResponse:
    """The response is the only time the key is shown: only its hash is
    stored, so a lost key must be revoked and reissued."""
    key, plaintext = ApiKeyRepository.create(
        client_id=client_id, input=input, user=user, session=session
    )
    session.commit()
    session.refresh(key)
    # The body carries a secret: keep it out of browser and proxy caches.
    response.headers["Cache-Control"] = "no-store"
    return ApiKeyCreatedResponse.from_created(key, plaintext)


@router.post(
    "/api-clients/{client_id}/keys/via-link", status_code=status.HTTP_201_CREATED
)
def create_api_key_via_link(
    client_id: int,
    input: ApiKeyViaLinkRegister,
    user: UserDep,
    session: SessionDep,
    response: Response,
) -> ApiKeyLinkCreatedResponse:
    """Issue a key for one-time delivery by link (see docs/API_KEYS.md,
    "Entrega por link"). The key is sealed into the link and never returned
    here: only the partner sees it, once. The token in the response is the
    only copy of the link's secret."""
    key, plaintext = ApiKeyRepository.create(
        client_id=client_id, input=input, user=user, session=session
    )
    link, token = ApiKeyDeliveryLinkRepository.create_for_key(
        key=key,
        plaintext=plaintext,
        ttl=timedelta(hours=input.link_ttl_hours),
        user=user,
        session=session,
    )
    del plaintext
    session.commit()
    session.refresh(key)
    session.refresh(link)
    response.headers["Cache-Control"] = "no-store"
    return ApiKeyLinkCreatedResponse.from_created(key, link, token)


@router.patch("/api-key-delivery-links/{delivery_link_id}/invalidate")
def invalidate_api_key_delivery_link(
    delivery_link_id: int, user: UserDep, session: SessionDep
) -> ApiKeyDeliveryLinkResponse:
    """Kill a link nobody opened yet. Its key, which nobody received, is
    revoked with it."""
    link = ApiKeyDeliveryLinkRepository.invalidate(
        id=delivery_link_id, user=user, session=session
    )
    session.commit()
    session.refresh(link)
    invalidate_api_key_cache([link.api_key.public_id])
    return ApiKeyDeliveryLinkResponse.from_link(link)


@router.post("/api-keys/{key_id}/share-link/email")
def email_api_key_link(
    key_id: int, input: ApiKeyLinkEmailSend, user: UserDep, session: SessionDep
) -> ApiKeyDeliveryLinkResponse:
    """Email the key's one-time link to its client's contact. Only the link
    goes out, never the key. The server never stores the token, so the
    admin's screen sends it back; it is checked (without consuming the
    link) and the URL is always built here, never taken from the client."""
    key = ApiKeyRepository.get_by_id(id=key_id, session=session)
    link = ApiKeyDeliveryLinkRepository.get_pending_for_key(key=key, token=input.token)
    url = delivery_link_url(link.link_id, input.token)
    try:
        sent_to = EmailService.send_api_key_link_email(
            to=[key.client.contact_email],
            data=ApiKeyLinkMail.from_link(link, url, input.message),
        )
    except Exception as e:
        logger.error(f"Failed to email API key link {link.link_id}: {e}")
        raise ApiKeyLinkEmailFailed() from e
    ApiKeyDeliveryLinkRepository.mark_emailed(
        link=link, to=sent_to, user=user, session=session
    )
    session.commit()
    session.refresh(link)
    logger.info(f"Emailed API key link {link.link_id} to {', '.join(sent_to)}")
    return ApiKeyDeliveryLinkResponse.from_link(link)


@router.get("/api-keys/{key_id}")
def get_api_key(key_id: int, session: SessionDep) -> ApiKeyResponse:
    key = ApiKeyRepository.get_by_id(id=key_id, session=session)
    return ApiKeyResponse.from_api_key(key)


@router.put("/api-keys/{key_id}")
def update_api_key(
    key_id: int, input: ApiKeyUpdate, session: SessionDep
) -> ApiKeyResponse:
    key = ApiKeyRepository.update(id=key_id, input=input, session=session)
    session.commit()
    session.refresh(key)
    invalidate_api_key_cache([key.public_id])
    return ApiKeyResponse.from_api_key(key)


@router.put("/api-keys/{key_id}/rate-limits")
def set_api_key_rate_limits(
    key_id: int, input: ApiKeyRateLimitsUpdate, session: SessionDep
) -> ApiKeyResponse:
    """Replace the key's limits; an empty list falls back to the defaults."""
    key = ApiKeyRepository.set_rate_limits(
        id=key_id, limits=input.rate_limits, session=session
    )
    session.commit()
    session.refresh(key)
    invalidate_api_key_cache([key.public_id])
    return ApiKeyResponse.from_api_key(key)


@router.patch("/api-keys/{key_id}/revoke")
def revoke_api_key(
    key_id: int, input: ApiKeyRevoke, user: UserDep, session: SessionDep
) -> ApiKeyResponse:
    """Final: a revoked key can't be reactivated or edited; issue a new one."""
    key = ApiKeyRepository.revoke(
        id=key_id, reason=input.reason, user=user, session=session
    )
    session.commit()
    session.refresh(key)
    # Takes effect on the very next request, not after the cache TTL.
    invalidate_api_key_cache([key.public_id])
    return ApiKeyResponse.from_api_key(key)


class ApiKeyLinkEmailFailed(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_502_BAD_GATEWAY,
            "Falha ao enviar o e-mail com o link; tente novamente",
        )
