"""Caps how many JupiterWeb crawls (one headless Chromium each, 200-500 MB)
run at once on this host, so a burst of users importing their schedules
can't OOM the VM and take Postgres down with it.

The slots are `flock`s on files in a directory every gunicorn worker of the
host shares, so the cap is global to the host without needing Redis, and
the kernel drops a lock the moment its worker dies: a crashed or killed
worker can never leave a slot stuck. Linux ties `flock` to the open file
description, so two coroutines of the same worker also exclude each other.
"""

import asyncio
import fcntl
import hashlib
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from server.config import CONFIG

SLOT_POLL_INTERVAL_SECONDS = 0.25
# Per-account locks hash into a fixed set of files, so the directory never
# grows. With only a couple of crawls running, a collision is negligible.
ACCOUNT_LOCK_BUCKETS = 1024


class JupiterCrawlLimitError(Exception):
    status_code: int = 503
    retry_after_seconds: int | None = None

    def headers(self) -> dict[str, str] | None:
        if self.retry_after_seconds is None:
            return None
        return {"Retry-After": str(self.retry_after_seconds)}


class JupiterCrawlerBusy(JupiterCrawlLimitError):
    status_code = 503
    retry_after_seconds = 30

    def __init__(self) -> None:
        super().__init__(
            "Muitas pessoas estão importando a grade agora. "
            "Tente novamente em alguns instantes."
        )


class JupiterCrawlAlreadyRunning(JupiterCrawlLimitError):
    status_code = 409

    def __init__(self) -> None:
        super().__init__(
            "Já existe uma importação da grade em andamento para este número USP."
        )


class JupiterCrawlTimeout(JupiterCrawlLimitError):
    status_code = 504

    def __init__(self) -> None:
        super().__init__(
            "O JupiterWeb demorou demais para responder. Tente novamente mais tarde."
        )


def _lock_dir() -> Path:
    path = Path(CONFIG.jupiter_crawl_lock_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _try_lock(path: Path) -> int | None:
    """Non-blocking exclusive lock; the open fd on success, None if taken."""
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    return fd


def _release(fd: int) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _account_lock_path(account: str) -> Path:
    # Hashed: the lock directory must not list who uses the feature.
    digest = hashlib.sha256(account.encode()).digest()
    bucket = int.from_bytes(digest[:4], "big") % ACCOUNT_LOCK_BUCKETS
    return _lock_dir() / f"account-{bucket}.lock"


async def _acquire_slot() -> int:
    """Waits up to `jupiter_crawl_queue_seconds` for a free slot."""
    lock_dir = _lock_dir()
    slots = [
        lock_dir / f"slot-{i}.lock"
        for i in range(max(1, CONFIG.jupiter_crawl_max_concurrent))
    ]
    deadline = time.monotonic() + CONFIG.jupiter_crawl_queue_seconds
    while True:
        for slot in slots:
            fd = _try_lock(slot)
            if fd is not None:
                return fd
        if time.monotonic() >= deadline:
            raise JupiterCrawlerBusy()
        await asyncio.sleep(SLOT_POLL_INTERVAL_SECONDS)


@asynccontextmanager
async def crawl_slot(account: str) -> AsyncIterator[None]:
    """Holds one host-wide crawl slot (and the account's lock) for the
    duration of the block.

    Raises `JupiterCrawlAlreadyRunning` right away when the same account
    already has a crawl in progress, and `JupiterCrawlerBusy` when no slot
    frees up within the queue time."""
    account_fd = _try_lock(_account_lock_path(account))
    if account_fd is None:
        raise JupiterCrawlAlreadyRunning()
    try:
        slot_fd = await _acquire_slot()
        try:
            yield
        finally:
            _release(slot_fd)
    finally:
        _release(account_fd)
