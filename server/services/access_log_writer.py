"""Buffers `ApiAccessLog` rows and writes them in batches (see docs/LOGGING.md).

`LoggerMiddleware` used to open a Session and commit one row inside the
request for every error response, on the event loop: each 4xx/5xx blocked
the whole worker for a database round trip, and a flood of 404s turned into
one INSERT per request. Now the middleware only calls `enqueue` (O(1), never
raises, never blocks) and a background task (`run_periodic_flush`, started
by the app lifespan) writes what accumulated in one transaction, off the
event loop, every `ACCESS_LOG_FLUSH_SECONDS` or as soon as
`ACCESS_LOG_FLUSH_BATCH` rows are waiting.

Under a flood it sheds load instead of queueing it:
- at most `ACCESS_LOG_MAX_PER_IP_PER_MINUTE` rows per client per minute; the
  rest of that minute becomes one summary row tagged `ErrorFlood`;
- at most `ACCESS_LOG_BUFFER_MAX` rows waiting; past it rows are dropped and
  the count is logged on the next flush.
"""

import asyncio
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime

from sqlmodel import Session

from server.config import CONFIG
from server.db import engine
from server.logger import logger
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.services.rate_limiter import client_identity
from server.utils.enums.api_security_level_enum import APISecurityLevel

ERROR_FLOOD_TAG = "ErrorFlood"
IP_WINDOW_SECONDS = 60
# Distinct clients tracked per window. Past it new clients aren't capped
# (the buffer bound still applies), so the map itself can't grow unbounded.
MAX_TRACKED_CLIENTS = 50_000


@dataclass(frozen=True)
class AccessLogRow:
    """Everything `ApiAccessLogRepository.create` needs, captured in the
    request (the ORM user/route objects must not outlive it)."""

    security_level: APISecurityLevel
    endpoint: str
    method: str
    status_code: int
    ip_address: str | None
    user_agent: str | None
    response_time_ms: int | None
    tags: list[str]
    user_id: int | None
    detail: str | None
    request_body: str | None
    api_key_id: int | None
    timestamp: datetime


@dataclass
class _ClientWindow:
    started_at: float
    count: int = 0
    suppressed: int = 0
    last_suppressed: AccessLogRow | None = None


@dataclass
class _Drained:
    rows: list[AccessLogRow] = field(default_factory=list)
    dropped: int = 0


def default_session_factory() -> Session:
    return Session(engine)


class AccessLogWriter:
    def __init__(
        self,
        *,
        max_buffer: int,
        batch_size: int,
        max_per_client_per_minute: int,
        session_factory: Callable[[], Session] = default_session_factory,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_buffer = max(max_buffer, 1)
        self.batch_size = max(batch_size, 1)
        self.max_per_client = max_per_client_per_minute
        self.session_factory = session_factory
        self.clock = clock
        self._buffer: deque[AccessLogRow] = deque()
        self._clients: dict[str, _ClientWindow] = {}
        self._dropped = 0
        self._lock = threading.Lock()
        self._wakeup: asyncio.Event | None = None
        self._flush_lock: asyncio.Lock | None = None

    @property
    def pending(self) -> int:
        return len(self._buffer)

    def enqueue(
        self,
        row: AccessLogRow,
        *,
        capped: bool = True,
        request_body: Callable[[], str | None] | None = None,
    ) -> None:
        """Called from the request. `capped=False` skips the per-client cap
        (for rows already limited upstream, like the first 429 per window).
        `request_body` is called only for an admitted row, so a suppressed
        request never pays for decoding and redacting its body."""
        with self._lock:
            admitted = not capped or self._admit(row)
        if not admitted:
            return
        if request_body is not None:
            try:
                row = replace(row, request_body=request_body())
            except Exception as e:
                logger.error(f"Error reading request body for access log: {e}")
        with self._lock:
            self._append(row)
            full_batch = len(self._buffer) >= self.batch_size
        if full_batch and self._wakeup is not None:
            self._wakeup.set()

    def _append(self, row: AccessLogRow) -> None:
        if len(self._buffer) >= self.max_buffer:
            self._dropped += 1
            return
        self._buffer.append(row)

    def _admit(self, row: AccessLogRow) -> bool:
        if self.max_per_client <= 0 or row.ip_address is None:
            return True
        key = client_identity(row.ip_address)
        now = self.clock()
        window = self._clients.get(key)
        if window is None or now - window.started_at >= IP_WINDOW_SECONDS:
            if window is not None:
                self._close_window(window)
            elif len(self._clients) >= MAX_TRACKED_CLIENTS:
                return True
            window = _ClientWindow(started_at=now)
            self._clients[key] = window
        if window.count < self.max_per_client:
            window.count += 1
            return True
        window.suppressed += 1
        window.last_suppressed = row
        return False

    def _close_window(self, window: _ClientWindow) -> None:
        """Turns a window's suppressed rows into one summary row, modelled
        on the last one (its endpoint, status and time)."""
        if window.suppressed == 0 or window.last_suppressed is None:
            return
        last = window.last_suppressed
        self._append(
            replace(
                last,
                tags=[*last.tags, ERROR_FLOOD_TAG],
                detail=(
                    f"{window.suppressed} respostas de erro deste cliente "
                    f"omitidas em {IP_WINDOW_SECONDS}s (limite: "
                    f"{self.max_per_client} por minuto); esta é a última"
                ),
                request_body=None,
            )
        )
        window.suppressed = 0
        window.last_suppressed = None

    def _close_expired_windows(self, *, force: bool) -> None:
        now = self.clock()
        for key, window in list(self._clients.items()):
            if force or now - window.started_at >= IP_WINDOW_SECONDS:
                self._close_window(window)
                del self._clients[key]

    def _drain(self, *, final: bool) -> _Drained:
        with self._lock:
            self._close_expired_windows(force=final)
            drained = _Drained(dropped=self._dropped)
            self._dropped = 0
            while self._buffer and len(drained.rows) < self.batch_size:
                drained.rows.append(self._buffer.popleft())
            return drained

    def write_rows(self, rows: list[AccessLogRow]) -> None:
        """One transaction for the whole batch. Blocking: run it in a thread.
        A failed batch is logged and discarded (retrying would pile up rows
        while the database is down)."""
        if not rows:
            return
        try:
            with self.session_factory() as session:
                for row in rows:
                    ApiAccessLogRepository.create(
                        security_level=row.security_level,
                        endpoint=row.endpoint,
                        method=row.method,
                        status_code=row.status_code,
                        ip_address=row.ip_address,
                        user_agent=row.user_agent,
                        response_time_ms=row.response_time_ms,
                        tags=row.tags,
                        user_id=row.user_id,
                        detail=row.detail,
                        request_body=row.request_body,
                        api_key_id=row.api_key_id,
                        timestamp=row.timestamp,
                        session=session,
                    )
                session.commit()
        except Exception as e:
            logger.error(f"Failed to persist {len(rows)} API access log rows: {e}")

    async def flush(self, *, final: bool = False) -> None:
        """Writes everything waiting, one batch per transaction. `final`
        also closes the open per-client windows (shutdown)."""
        if self._flush_lock is None:
            self._flush_lock = asyncio.Lock()
        async with self._flush_lock:
            while True:
                drained = self._drain(final=final)
                if drained.dropped:
                    logger.warning(
                        f"API access log buffer full: {drained.dropped} rows dropped"
                    )
                if not drained.rows:
                    return
                await asyncio.to_thread(self.write_rows, drained.rows)

    async def run_periodic_flush(self, interval_seconds: float) -> None:
        """Background task: flushes every `interval_seconds`, or sooner when
        a full batch is waiting. Cancel it, then call `flush(final=True)`."""
        self._wakeup = asyncio.Event()
        while True:
            try:
                await asyncio.wait_for(self._wakeup.wait(), timeout=interval_seconds)
            except TimeoutError:
                pass
            self._wakeup.clear()
            try:
                await self.flush()
            except Exception as e:
                logger.error(f"API access log flush failed: {e}")


ACCESS_LOG_WRITER = AccessLogWriter(
    max_buffer=CONFIG.access_log_buffer_max,
    batch_size=CONFIG.access_log_flush_batch,
    max_per_client_per_minute=CONFIG.access_log_max_per_ip_per_minute,
)
