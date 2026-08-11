from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from server.deps.authenticate import WebSocketIdentityDep
from server.models.http.requests.online_request_models import OnlineClientMessage
from server.services.online_presence_service import (
    heartbeat,
    register_connection,
    unregister_connection,
)

router = APIRouter(tags=["Online"])


@router.websocket("/online/ws")
async def online_ws(websocket: WebSocket, user: WebSocketIdentityDep) -> None:
    """Register live presence. Anonymous connections are allowed - identity is
    resolved best-effort from the session cookie or a `?token=` query param.
    """
    await websocket.accept()
    connection_id = register_connection(
        websocket,
        ip_address=websocket.client.host if websocket.client else "unknown",
        user_agent=websocket.headers.get("user-agent", ""),
        user=user,
        page=None,
    )
    try:
        while True:
            raw = await websocket.receive_json()
            message = OnlineClientMessage.model_validate(raw)
            heartbeat(connection_id, page=message.page)
    except WebSocketDisconnect:
        pass
    finally:
        unregister_connection(connection_id)
