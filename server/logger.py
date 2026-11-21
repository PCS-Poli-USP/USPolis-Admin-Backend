"""App and Loki access loggers (see docs/LOGGING.md).

Records never touch the disk on the caller's thread: each logger has a
bounded `DroppingQueueHandler`, and a `QueueListener` thread per worker
process does the actual writes. A full queue drops the record instead of
blocking, so a burst of requests (or a slow disk) can't stall the event loop.

All gunicorn workers append to the same files, so the file handlers are
`LockedRotatingFileHandler`s, which serialize writes and rotations across
processes with `flock`.
"""

import atexit
import fcntl
import logging
import os
import queue
import threading
import time
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path

from server.config import CONFIG

current_dir = Path(__file__).resolve()
log_dir = current_dir.parent.parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "api.log"
loki_log_file = log_dir / "loki-access-api.log"

DROPPED_REPORT_INTERVAL_SECONDS = 60


class LockedRotatingFileHandler(RotatingFileHandler):
    """`RotatingFileHandler` that is safe with several processes on one file.

    The stock handler rotates per process: when worker A renames `api.log`
    to `api.log.1`, worker B keeps writing to its old descriptor (now the
    `.1`) and measures size with its own `tell()`, so rotations repeat and
    backups get overwritten. Here every emit, under an exclusive `flock` on
    `<file>.lock`:

    - reopens the stream when the file on disk is no longer the one this
      process has open (another process rotated it);
    - decides on rollover from the real size on disk (`os.stat`);
    - rotates and writes (the base `emit` flushes) before unlocking.

    The kernel drops a `flock` when its process dies, so a killed worker
    can't leave the lock held. Linux/Unix only (`fcntl`).
    """

    def __init__(
        self, filename: str | Path, *, max_bytes: int, backup_count: int
    ) -> None:
        super().__init__(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
            delay=True,
        )
        self.lock_path = f"{self.baseFilename}.lock"
        self._lock_fd: int | None = None
        self._lock_pid: int | None = None
        self._stream_id: tuple[int, int] | None = None

    def _open(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        stream = super()._open()
        stat = os.fstat(stream.fileno())
        self._stream_id = (stat.st_dev, stat.st_ino)
        return stream

    def _get_lock_fd(self) -> int:
        # A forked child shares the parent's open file description, and
        # flock locks belong to it: the child needs its own to exclude it.
        if self._lock_fd is None or self._lock_pid != os.getpid():
            self._lock_fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, 0o644)
            self._lock_pid = os.getpid()
        return self._lock_fd

    def _reopen_if_rotated(self) -> None:
        if self.stream is None:
            return
        try:
            stat = os.stat(self.baseFilename)
            on_disk: tuple[int, int] | None = (stat.st_dev, stat.st_ino)
        except FileNotFoundError:
            on_disk = None
        if on_disk != self._stream_id:
            self.stream.close()
            self.stream = None  # reopened by emit

    def shouldRollover(self, record: logging.LogRecord) -> bool:  # noqa: N802
        if self.maxBytes <= 0:
            return False
        try:
            size = os.stat(self.baseFilename).st_size
        except FileNotFoundError:
            return False
        # An empty file is never rotated, even for a record over maxBytes.
        if size == 0:
            return False
        message = f"{self.format(record)}\n"
        return size + len(message.encode("utf-8", "replace")) >= self.maxBytes

    def emit(self, record: logging.LogRecord) -> None:
        try:
            fd = self._get_lock_fd()
            fcntl.flock(fd, fcntl.LOCK_EX)
        except Exception:
            self.handleError(record)
            return
        try:
            self._reopen_if_rotated()
            super().emit(record)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)


class DroppingQueueHandler(QueueHandler):
    """`QueueHandler` over a bounded queue that drops instead of blocking.

    Drops are counted, and reported with one WARNING record at most every
    `DROPPED_REPORT_INTERVAL_SECONDS`, sent as soon as the queue has room.
    """

    def __init__(self, log_queue: "queue.Queue[logging.LogRecord]", name: str):
        super().__init__(log_queue)
        self.logger_name = name
        self.dropped = 0
        self._dropped_lock = threading.Lock()
        self._last_report = 0.0

    def enqueue(self, record: logging.LogRecord) -> None:
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            with self._dropped_lock:
                self.dropped += 1
            return
        self._report_dropped()

    def _report_dropped(self) -> None:
        if not self.dropped:
            return
        now = time.monotonic()
        if now - self._last_report < DROPPED_REPORT_INTERVAL_SECONDS:
            return
        with self._dropped_lock:
            dropped, self.dropped = self.dropped, 0
            self._last_report = now
        report = logging.LogRecord(
            name=self.logger_name,
            level=logging.WARNING,
            pathname=__file__,
            lineno=0,
            msg=f"Log queue full: {dropped} records dropped",
            args=None,
            exc_info=None,
        )
        try:
            self.queue.put_nowait(report)
        except queue.Full:
            with self._dropped_lock:
                self.dropped += dropped


class QueuedLogger:
    """A bounded queue, the handler feeding it and the listener draining it."""

    def __init__(self, name: str, handlers: list[logging.Handler]) -> None:
        self.handlers = handlers
        self.queue_handler = DroppingQueueHandler(self._new_queue(), name)
        self.listener = self._new_listener()

    @staticmethod
    def _new_queue() -> "queue.Queue[logging.LogRecord]":
        return queue.Queue(maxsize=max(CONFIG.log_queue_max_size, 1))

    def _new_listener(self) -> QueueListener:
        return QueueListener(
            self.queue_handler.queue, *self.handlers, respect_handler_level=True
        )

    @property
    def running(self) -> bool:
        return self.listener._thread is not None  # pyright: ignore[reportAttributeAccessIssue]

    def start(self) -> None:
        if not self.running:
            self.listener.start()

    def stop(self) -> None:
        """Writes everything still queued, then stops the thread."""
        if self.running:
            self.listener.stop()

    def restart_after_fork(self) -> None:
        """Threads don't survive fork: a child starts its own listener on a
        fresh queue (the inherited one may hold a lock taken mid-fork)."""
        self.queue_handler.queue = self._new_queue()
        self.listener = self._new_listener()
        self.listener.start()


formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

size_handler = LockedRotatingFileHandler(
    log_file,
    max_bytes=CONFIG.log_max_size,
    backup_count=CONFIG.log_backup_count,
)
size_handler.setFormatter(formatter)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# LOKI LOGGER
loki_access_logger = logging.getLogger("loki_access")
loki_access_logger.setLevel(logging.INFO)
loki_access_logger.propagate = False

# Handler que envia para o arquivo (rotaciona a cada 10MB)
loki_file_handler = LockedRotatingFileHandler(
    loki_log_file, max_bytes=10485760, backup_count=5
)

# Formato do log: [Data] [Nível] [IP] [Método] [Path] [Status]
loki_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s client_ip="%(client_ip)s" method="%(method)s" path="%(path)s" status="%(status_code)s" duration="%(duration).3f" email="%(email)s"',
    datefmt="%Y-%m-%d %H:%M:%S",
)
loki_file_handler.setFormatter(loki_formatter)

queued_loggers: list[QueuedLogger] = []

if not logger.hasHandlers():
    app_handlers: list[logging.Handler] = [size_handler]
    if CONFIG.debug:
        app_handlers.insert(0, stream_handler)
    app_queue = QueuedLogger("app_logger", app_handlers)
    logger.addHandler(app_queue.queue_handler)
    queued_loggers.append(app_queue)

if not loki_access_logger.hasHandlers():
    loki_queue = QueuedLogger("loki_access", [loki_file_handler])
    loki_access_logger.addHandler(loki_queue.queue_handler)
    queued_loggers.append(loki_queue)


def start_log_listeners() -> None:
    for queued in queued_loggers:
        queued.start()


def stop_log_listeners() -> None:
    """Writes what is still queued and stops every listener. Registered with
    `atexit` after `logging` registered `logging.shutdown`, so it runs
    first."""
    for queued in queued_loggers:
        queued.stop()


def _restart_listeners_after_fork() -> None:
    for queued in queued_loggers:
        queued.restart_after_fork()


start_log_listeners()
atexit.register(stop_log_listeners)
os.register_at_fork(after_in_child=_restart_listeners_after_fork)
