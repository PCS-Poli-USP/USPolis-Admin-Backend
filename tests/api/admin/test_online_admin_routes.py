from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from starlette.websockets import WebSocketDisconnect
from sqlmodel import Session

import server.services.online_presence_service as presence_service
from server.app import app
from server.db import get_db
from server.models.database.user_db_model import User
from server.repositories.user_session_repository import UserSessionRepository


@pytest.fixture(autouse=True)
def _reset_presence_state() -> Generator[None, None, None]:
    presence_service._connections.clear()
    presence_service._admin_listeners.clear()
    presence_service._pending.clear()
    yield
    presence_service._connections.clear()
    presence_service._admin_listeners.clear()
    presence_service._pending.clear()


@pytest.fixture(name="ws_client")
def ws_client_fixture(session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _session_cookie(user: User, session: Session) -> dict[str, str]:
    user_session = UserSessionRepository.create_session(
        user_id=user.id, user_agent="pytest", ip_address="127.0.0.1", session=session
    )
    session.commit()
    return {"session": user_session.id}


def test_anonymous_connection_is_rejected(ws_client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with ws_client.websocket_connect("/admin/online/ws"):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


def test_non_admin_connection_is_rejected(
    ws_client: TestClient, common_user: User, session: Session
) -> None:
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with ws_client.websocket_connect(
            "/admin/online/ws", cookies=_session_cookie(common_user, session)
        ):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


def test_admin_connection_receives_initial_snapshot(
    ws_client: TestClient, user: User, session: Session
) -> None:
    with ws_client.websocket_connect(
        "/admin/online/ws", cookies=_session_cookie(user, session)
    ) as admin_ws:
        message = admin_ws.receive_json()

    assert message == {"event": "snapshot", "connections": []}
