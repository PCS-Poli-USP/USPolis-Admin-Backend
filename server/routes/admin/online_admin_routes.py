from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from server.deps.authenticate import WebSocketIdentityDep
from server.models.http.responses.online_response_models import OnlineSnapshotEvent
from server.services.online_presence_service import (
    register_admin_listener,
    snapshot,
    unregister_admin_listener,
)

router = APIRouter(prefix="/admin", tags=["Online", "Admin"])


@router.websocket("/online/ws")
async def admin_online_ws(websocket: WebSocket, user: WebSocketIdentityDep) -> None:
    """Read-only live feed of online connections for admins.

    Sends a full snapshot once on connect, then batched diffs pushed by
    `online_presence_service.flush_pending_diff`. Accepts no client messages.
    """
    if user is None or not user.is_admin:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    register_admin_listener(websocket)
    await websocket.send_json(
        OnlineSnapshotEvent(connections=snapshot()).model_dump(mode="json")
    )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        unregister_admin_listener(websocket)
