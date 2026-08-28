import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from server.services.cron.scheduler import (
    cancel_task,
    lifespan,
    periodic_cache_cleanup,
    periodic_daily_tasks,
)

_real_sleep = asyncio.sleep


async def _fast_sleep(_seconds: float) -> None:
    """Replaces the module's real 3600s/24h sleeps with a genuine (but
    real, not mocked) zero-second sleep, so the loop still actually yields
    to the event loop between iterations - a plain no-yield AsyncMock would
    let `while True` spin forever with no checkpoint where cancellation
    could ever be delivered, hanging the test. Calls the real asyncio.sleep
    captured before patching, since `scheduler.asyncio` is the same module
    object as `asyncio` itself - patching `asyncio.sleep` through it would
    otherwise also patch this helper's own call, recursing forever."""
    await _real_sleep(0)


@pytest.mark.asyncio
async def test_cancel_task_with_none_does_nothing() -> None:
    await cancel_task(None)


@pytest.mark.asyncio
async def test_cancel_task_cancels_a_running_task() -> None:
    async def forever() -> None:
        while True:
            await asyncio.sleep(3600)

    task = asyncio.create_task(forever())
    await asyncio.sleep(0)  # let it actually start running

    await cancel_task(task)

    assert task.cancelled()


@pytest.mark.asyncio
async def test_periodic_cache_cleanup_clears_cache_on_each_tick() -> None:
    with (
        patch(
            "server.services.cron.scheduler.asyncio.sleep", side_effect=_fast_sleep
        ),
        patch(
            "server.services.cron.scheduler.clear_expired_cache", return_value=3
        ) as mock_clear,
    ):
        task = asyncio.create_task(periodic_cache_cleanup())
        for _ in range(5):
            await _real_sleep(0)
        await cancel_task(task)

    assert mock_clear.call_count > 0


@pytest.mark.asyncio
async def test_periodic_daily_tasks_runs_run_daily_tasks_on_each_tick() -> None:
    with (
        patch(
            "server.services.cron.scheduler.asyncio.sleep", side_effect=_fast_sleep
        ),
        patch("server.services.cron.scheduler.run_daily_tasks") as mock_run,
    ):
        task = asyncio.create_task(periodic_daily_tasks())
        for _ in range(5):
            await _real_sleep(0)
        await cancel_task(task)

    assert mock_run.call_count > 0


@pytest.mark.asyncio
async def test_lifespan_starts_and_stops_background_tasks_cleanly() -> None:
    with patch(
        "server.services.cron.scheduler.asyncio.sleep", side_effect=_fast_sleep
    ):
        app = MagicMock(spec=FastAPI)
        async with lifespan(app):
            await _real_sleep(0)
        # Reaching here means both background tasks were created, cancelled
        # and awaited without the CancelledError leaking out of lifespan().
