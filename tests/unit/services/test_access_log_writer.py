import asyncio
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from server.services.access_log_writer import (
    ERROR_FLOOD_TAG,
    IP_WINDOW_SECONDS,
    AccessLogRow,
    AccessLogWriter,
)
from server.utils.enums.api_security_level_enum import APISecurityLevel

TIMESTAMP = datetime(2026, 11, 20, 12, 0)


def make_row(ip: str | None = "143.107.1.1", **overrides: object) -> AccessLogRow:
    values: dict[str, object] = {
        "security_level": APISecurityLevel.PUBLIC,
        "endpoint": "/classrooms/999",
        "method": "GET",
        "status_code": 404,
        "ip_address": ip,
        "user_agent": "pytest",
        "response_time_ms": 3,
        "tags": ["Public"],
        "user_id": None,
        "detail": "not found",
        "request_body": None,
        "api_key_id": None,
        "timestamp": TIMESTAMP,
    }
    values.update(overrides)
    return AccessLogRow(**values)  # type: ignore[arg-type]


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class FakeSessions:
    """Session factory recording each transaction's rows and commits."""

    def __init__(self) -> None:
        self.transactions: list[list[object]] = []
        self.fail = False

    def __call__(self) -> MagicMock:
        added: list[object] = []
        session = MagicMock()
        session.__enter__.return_value = session
        session.add.side_effect = added.append

        def commit() -> None:
            if self.fail:
                raise RuntimeError("database is down")
            self.transactions.append(added)

        session.commit.side_effect = commit
        return session

    @property
    def rows(self) -> list[object]:
        return [row for transaction in self.transactions for row in transaction]


def make_writer(
    sessions: FakeSessions,
    clock: FakeClock | None = None,
    *,
    max_buffer: int = 100,
    batch_size: int = 10,
    max_per_client: int = 5,
) -> AccessLogWriter:
    return AccessLogWriter(
        max_buffer=max_buffer,
        batch_size=batch_size,
        max_per_client_per_minute=max_per_client,
        session_factory=sessions,
        clock=clock or FakeClock(),
    )


class TestBatching:
    def test_enqueue_only_buffers(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions)

        writer.enqueue(make_row())

        assert writer.pending == 1
        assert sessions.transactions == []

    def test_flush_writes_one_transaction_per_batch(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions, batch_size=10, max_per_client=0)
        for _ in range(25):
            writer.enqueue(make_row())

        asyncio.run(writer.flush())

        assert [len(t) for t in sessions.transactions] == [10, 10, 5]
        assert writer.pending == 0

    def test_keeps_the_time_of_the_response(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions)
        writer.enqueue(make_row())

        asyncio.run(writer.flush())

        assert sessions.rows[0].timestamp == TIMESTAMP  # type: ignore[attr-defined]

    def test_a_failed_batch_is_logged_and_discarded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        error = MagicMock()
        monkeypatch.setattr("server.services.access_log_writer.logger.error", error)
        sessions = FakeSessions()
        sessions.fail = True
        writer = make_writer(sessions)
        writer.enqueue(make_row())

        asyncio.run(writer.flush())

        assert writer.pending == 0
        error.assert_called_once()
        assert "1 API access log rows" in error.call_args.args[0]

    def test_a_full_batch_wakes_the_periodic_flush(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions, batch_size=3, max_per_client=0)

        async def scenario() -> None:
            task = asyncio.create_task(writer.run_periodic_flush(3600))
            await asyncio.sleep(0)  # let it create its wakeup event
            for _ in range(3):
                writer.enqueue(make_row())
            for _ in range(50):
                if sessions.transactions:
                    break
                await asyncio.sleep(0.01)
            task.cancel()

        asyncio.run(scenario())

        assert [len(t) for t in sessions.transactions] == [3]


class TestBufferBound:
    def test_drops_past_the_buffer_and_reports_it(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        warning = MagicMock()
        monkeypatch.setattr("server.services.access_log_writer.logger.warning", warning)
        sessions = FakeSessions()
        writer = make_writer(sessions, max_buffer=3, max_per_client=0)
        for _ in range(5):
            writer.enqueue(make_row())

        assert writer.pending == 3
        asyncio.run(writer.flush())

        assert len(sessions.rows) == 3
        warning.assert_called_once()
        assert "2 rows dropped" in warning.call_args.args[0]


class TestPerClientCap:
    def test_rows_past_the_cap_become_one_summary_row(self) -> None:
        sessions = FakeSessions()
        clock = FakeClock()
        writer = make_writer(sessions, clock, max_per_client=2)
        for status in (404, 404, 404, 422, 403):
            writer.enqueue(make_row(status_code=status))

        assert writer.pending == 2
        clock.now += IP_WINDOW_SECONDS
        asyncio.run(writer.flush())

        rows = sessions.rows
        assert len(rows) == 3
        summary = rows[-1]
        assert ERROR_FLOOD_TAG in summary.tags  # type: ignore[attr-defined]
        assert summary.status_code == 403  # type: ignore[attr-defined]  # the last one
        assert summary.detail.startswith("3 respostas de erro")  # type: ignore[attr-defined]

    def test_the_open_window_is_summarized_on_the_final_flush(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions, max_per_client=1)
        for _ in range(4):
            writer.enqueue(make_row())

        asyncio.run(writer.flush())
        assert len(sessions.rows) == 1

        asyncio.run(writer.flush(final=True))
        assert len(sessions.rows) == 2
        assert ERROR_FLOOD_TAG in sessions.rows[1].tags  # type: ignore[attr-defined]

    def test_clients_are_capped_independently(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions, max_per_client=1)
        writer.enqueue(make_row(ip="1.1.1.1"))
        writer.enqueue(make_row(ip="2.2.2.2"))
        writer.enqueue(make_row(ip="1.1.1.1"))

        assert writer.pending == 2

    def test_ipv6_addresses_of_one_slash64_share_the_cap(self) -> None:
        writer = make_writer(FakeSessions(), max_per_client=1)
        writer.enqueue(make_row(ip="2001:db8::1"))
        writer.enqueue(make_row(ip="2001:db8::2"))

        assert writer.pending == 1

    def test_uncapped_rows_skip_the_cap(self) -> None:
        writer = make_writer(FakeSessions(), max_per_client=1)
        for _ in range(3):
            writer.enqueue(make_row(), capped=False)

        assert writer.pending == 3

    def test_the_body_is_only_read_for_admitted_rows(self) -> None:
        sessions = FakeSessions()
        writer = make_writer(sessions, max_per_client=1)
        body = MagicMock(return_value='{"code": "MAC0110"}')

        writer.enqueue(make_row(), request_body=body)
        writer.enqueue(make_row(), request_body=body)

        body.assert_called_once()
        asyncio.run(writer.flush())
        assert sessions.rows[0].request_body == '{"code": "MAC0110"}'  # type: ignore[attr-defined]
