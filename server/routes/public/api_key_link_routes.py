"""One-time API key delivery links, opened by partners (see docs/API_KEYS.md,
"Entrega por link").

The link is `<frontend>/api-key/<link_id>#<token>`. The frontend page calls GET
for the status and, only when the person clicks "Revelar chave", POSTs the
token from the URL fragment to /reveal. GET never consumes the link: chat
apps and email scanners fetch links to build previews.
"""

from typing import Annotated

from fastapi import APIRouter, Path, Request, Response

from server.deps.session_dep import SessionDep
from server.middlewares.request_utils import get_client_ip
from server.models.http.requests.api_key_request_models import ApiKeyLinkReveal
from server.models.http.responses.api_key_response_models import (
    ApiKeyLinkPublicResponse,
    ApiKeyRevealedResponse,
)
from server.repositories.api_key_delivery_link_repository import (
    ApiKeyDeliveryLinkRepository,
)

router = APIRouter(prefix="/api-key-links", tags=["API Key Links"])

LinkId = Annotated[str, Path(pattern=r"^[0-9a-f]{16}$")]


def _keep_private(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex"


@router.get("/{link_id}")
def get_api_key_link(
    link_id: LinkId, session: SessionDep, response: Response
) -> ApiKeyLinkPublicResponse:
    link = ApiKeyDeliveryLinkRepository.get_by_link_id(link_id=link_id, session=session)
    _keep_private(response)
    return ApiKeyLinkPublicResponse.from_link(link)


@router.post("/{link_id}/reveal")
def reveal_api_key_link(
    link_id: LinkId,
    input: ApiKeyLinkReveal,
    request: Request,
    response: Response,
    session: SessionDep,
) -> ApiKeyRevealedResponse:
    """The key, once: the link is consumed and its sealed copy wiped. 404
    for an unknown link or a wrong token (which leaves the link intact), 410
    once it was used, expired or was invalidated."""
    link, plaintext = ApiKeyDeliveryLinkRepository.reveal(
        link_id=link_id,
        token=input.token,
        ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        session=session,
    )
    session.commit()
    session.refresh(link)
    _keep_private(response)
    return ApiKeyRevealedResponse.from_revealed(link, plaintext)
