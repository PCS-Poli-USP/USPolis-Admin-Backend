import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import WebSocket

from server.models.database.user_db_model import User
from server.models.http.responses.online_response_models import (
    OnlineConnectionResponse,
    OnlineDiffEvent,
)
from server.utils.brazil_datetime import BrazilDatetime

HEARTBEAT_TIMEOUT_SECONDS = 60
REAPER_INTERVAL_SECONDS = 15
DIFF_FLUSH_INTERVAL_SECONDS = 5


@dataclass
class _ConnectionState:
    websocket: WebSocket
    connection_id: str
    user_id: int | None
    name: str | None
    email: str | None
    ip_address: str
    user_agent: str
    connected_since: datetime
    last_seen: datetime
    page: str | None


_connections: dict[str, _ConnectionState] = {}
_admin_listeners: set[WebSocket] = set()
_pending: dict[str, OnlineConnectionResponse | None] = {}


def _to_response(state: _ConnectionState) -> OnlineConnectionResponse:
    return OnlineConnectionResponse(
        connection_id=state.connection_id,
        user_id=state.user_id,
        name=state.name,
        email=state.email,
        ip_address=state.ip_address,
        user_agent=state.user_agent,
        connected_since=state.connected_since,
        page=state.page,
    )


def register_connection(
    websocket: WebSocket,
    *,
    ip_address: str,
    user_agent: str,
    user: User | None,
    page: str | None,
) -> str:
    connection_id = uuid.uuid4().hex
    now = BrazilDatetime.now_utc()
    state = _ConnectionState(
        websocket=websocket,
        connection_id=connection_id,
        user_id=user.id if user else None,
        name=user.name if user else None,
        email=user.email if user else None,
        ip_address=ip_address,
        user_agent=user_agent,
        connected_since=now,
        last_seen=now,
        page=page,
    )
    _connections[connection_id] = state
    _pending[connection_id] = _to_response(state)
    return connection_id


def heartbeat(connection_id: str, *, page: str | None) -> None:
    state = _connections.get(connection_id)
    if state is None:
        return
    state.last_seen = BrazilDatetime.now_utc()
    if page is not None and page != state.page:
        state.page = page
        _pending[connection_id] = _to_response(state)


def unregister_connection(connection_id: str) -> None:
    if _connections.pop(connection_id, None) is None:
        return
    _pending[connection_id] = None


def register_admin_listener(websocket: WebSocket) -> None:
    _admin_listeners.add(websocket)


def unregister_admin_listener(websocket: WebSocket) -> None:
    _admin_listeners.discard(websocket)


def snapshot() -> list[OnlineConnectionResponse]:
    return [_to_response(state) for state in _connections.values()]


async def flush_pending_diff() -> None:
    if not _pending:
        return
    upserted = [response for response in _pending.values() if response is not None]
    removed = [
        connection_id
        for connection_id, response in _pending.items()
        if response is None
    ]
    _pending.clear()
    if not upserted and not removed:
        return
    event = OnlineDiffEvent(upserted=upserted, removed=removed)
    payload = event.model_dump(mode="json")
    dead_listeners: list[WebSocket] = []
    for listener in _admin_listeners:
        try:
            await listener.send_json(payload)
        except Exception:
            dead_listeners.append(listener)
    for listener in dead_listeners:
        unregister_admin_listener(listener)


async def reap_stale_connections() -> None:
    now = BrazilDatetime.now_utc()
    stale_ids = [
        connection_id
        for connection_id, state in _connections.items()
        if now - state.last_seen > timedelta(seconds=HEARTBEAT_TIMEOUT_SECONDS)
    ]
    for connection_id in stale_ids:
        state = _connections.get(connection_id)
        unregister_connection(connection_id)
        if state is not None:
            try:
                await state.websocket.close()
            except Exception:
                pass
