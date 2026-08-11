from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
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


def test_anonymous_connect_is_visible_to_admin_as_anonymous(
    ws_client: TestClient, user: User, session: Session
) -> None:
    with ws_client.websocket_connect(
        "/admin/online/ws", cookies=_session_cookie(user, session)
    ) as admin_ws:
        assert admin_ws.receive_json() == {"event": "snapshot", "connections": []}

        with ws_client.websocket_connect("/online/ws"):
            ws_client.portal.call(presence_service.flush_pending_diff)
            diff = admin_ws.receive_json()

    assert diff["event"] == "diff"
    assert diff["removed"] == []
    assert len(diff["upserted"]) == 1
    entry = diff["upserted"][0]
    assert entry["user_id"] is None
    assert entry["ip_address"] == "testclient"


def test_authenticated_connect_resolves_identity(
    ws_client: TestClient, user: User, common_user: User, session: Session
) -> None:
    with ws_client.websocket_connect(
        "/admin/online/ws", cookies=_session_cookie(user, session)
    ) as admin_ws:
        admin_ws.receive_json()  # initial snapshot

        with ws_client.websocket_connect(
            "/online/ws", cookies=_session_cookie(common_user, session)
        ):
            ws_client.portal.call(presence_service.flush_pending_diff)
            diff = admin_ws.receive_json()

    entry = diff["upserted"][0]
    assert entry["user_id"] == common_user.id
    assert entry["name"] == common_user.name
    assert entry["email"] == common_user.email


def test_page_heartbeat_updates_entry_and_disconnect_removes_it(
    ws_client: TestClient, user: User, session: Session
) -> None:
    with ws_client.websocket_connect(
        "/admin/online/ws", cookies=_session_cookie(user, session)
    ) as admin_ws:
        admin_ws.receive_json()  # initial snapshot

        with ws_client.websocket_connect("/online/ws") as public_ws:
            public_ws.send_json({"page": "classroom-map"})
            ws_client.portal.call(presence_service.flush_pending_diff)
            diff = admin_ws.receive_json()
            assert diff["upserted"][0]["page"] == "classroom-map"
            connection_id = diff["upserted"][0]["connection_id"]

        ws_client.portal.call(presence_service.flush_pending_diff)
        removal_diff = admin_ws.receive_json()

    assert removal_diff["removed"] == [connection_id]
    assert removal_diff["upserted"] == []
