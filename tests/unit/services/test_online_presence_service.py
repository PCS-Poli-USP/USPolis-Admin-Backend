from collections.abc import Generator
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

import server.services.online_presence_service as presence_service
from server.models.database.user_db_model import User
from server.utils.brazil_datetime import BrazilDatetime


@pytest.fixture(autouse=True)
def _reset_presence_state() -> Generator[None, None, None]:
    presence_service._connections.clear()
    presence_service._admin_listeners.clear()
    presence_service._pending.clear()
    yield
    presence_service._connections.clear()
    presence_service._admin_listeners.clear()
    presence_service._pending.clear()


def make_user(*, user_id: int = 1) -> User:
    return User(id=user_id, email="user@usp.br", name="Test User", is_admin=False)


def test_register_connection_queues_an_upsert() -> None:
    connection_id = presence_service.register_connection(
        MagicMock(),
        ip_address="203.0.113.5",
        user_agent="pytest",
        user=None,
        page=None,
    )

    assert connection_id in presence_service._connections
    assert presence_service._pending[connection_id] is not None
    assert presence_service._pending[connection_id].ip_address == "203.0.113.5"
    assert presence_service._pending[connection_id].user_id is None


def test_register_connection_captures_authenticated_identity() -> None:
    user = make_user()
    connection_id = presence_service.register_connection(
        MagicMock(),
        ip_address="203.0.113.5",
        user_agent="pytest",
        user=user,
        page=None,
    )

    entry = presence_service._pending[connection_id]
    assert entry is not None
    assert entry.user_id == user.id
    assert entry.name == user.name
    assert entry.email == user.email


def test_heartbeat_with_changed_page_queues_an_upsert() -> None:
    connection_id = presence_service.register_connection(
        MagicMock(), ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )
    presence_service._pending.clear()

    presence_service.heartbeat(connection_id, page="classroom-map")

    entry = presence_service._pending[connection_id]
    assert entry is not None
    assert entry.page == "classroom-map"


def test_heartbeat_with_unchanged_page_does_not_queue() -> None:
    connection_id = presence_service.register_connection(
        MagicMock(),
        ip_address="203.0.113.5",
        user_agent="pytest",
        user=None,
        page="classroom-map",
    )
    presence_service._pending.clear()

    presence_service.heartbeat(connection_id, page="classroom-map")
    presence_service.heartbeat(connection_id, page=None)

    assert presence_service._pending == {}


def test_unregister_connection_queues_a_removal() -> None:
    connection_id = presence_service.register_connection(
        MagicMock(), ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )
    presence_service._pending.clear()

    presence_service.unregister_connection(connection_id)

    assert connection_id not in presence_service._connections
    assert presence_service._pending[connection_id] is None


def test_connect_then_disconnect_within_same_window_collapses_to_removal() -> None:
    connection_id = presence_service.register_connection(
        MagicMock(), ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )

    presence_service.unregister_connection(connection_id)

    assert presence_service._pending[connection_id] is None


@pytest.mark.asyncio
async def test_flush_pending_diff_batches_multiple_changes_into_one_message() -> None:
    listener = AsyncMock()
    presence_service.register_admin_listener(listener)

    connected_id = presence_service.register_connection(
        MagicMock(), ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )
    other_id = presence_service.register_connection(
        MagicMock(), ip_address="198.51.100.9", user_agent="pytest", user=None, page=None
    )
    presence_service.unregister_connection(other_id)

    await presence_service.flush_pending_diff()

    assert listener.send_json.await_count == 1
    payload = listener.send_json.await_args.args[0]
    assert payload["event"] == "diff"
    assert [entry["connection_id"] for entry in payload["upserted"]] == [connected_id]
    assert payload["removed"] == [other_id]
    assert presence_service._pending == {}


@pytest.mark.asyncio
async def test_flush_pending_diff_sends_nothing_when_no_changes() -> None:
    listener = AsyncMock()
    presence_service.register_admin_listener(listener)

    await presence_service.flush_pending_diff()

    listener.send_json.assert_not_awaited()


@pytest.mark.asyncio
async def test_flush_pending_diff_drops_a_dead_listener() -> None:
    dead_listener = AsyncMock()
    dead_listener.send_json.side_effect = RuntimeError("connection closed")
    presence_service.register_admin_listener(dead_listener)

    presence_service.register_connection(
        MagicMock(), ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )

    await presence_service.flush_pending_diff()

    assert dead_listener not in presence_service._admin_listeners


@pytest.mark.asyncio
async def test_reap_stale_connections_removes_and_closes_timed_out_sockets() -> None:
    websocket = AsyncMock()
    connection_id = presence_service.register_connection(
        websocket, ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )
    stale_state = presence_service._connections[connection_id]
    stale_state.last_seen = BrazilDatetime.now_utc() - timedelta(
        seconds=presence_service.HEARTBEAT_TIMEOUT_SECONDS + 1
    )

    await presence_service.reap_stale_connections()

    assert connection_id not in presence_service._connections
    assert presence_service._pending[connection_id] is None
    websocket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_reap_stale_connections_keeps_recently_seen_connections() -> None:
    websocket = AsyncMock()
    connection_id = presence_service.register_connection(
        websocket, ip_address="203.0.113.5", user_agent="pytest", user=None, page=None
    )

    await presence_service.reap_stale_connections()

    assert connection_id in presence_service._connections
    websocket.close.assert_not_awaited()
