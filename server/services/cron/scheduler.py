import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI

from server.cache import clear_expired_cache
from server.config import CONFIG
from server.services.access_log_writer import ACCESS_LOG_WRITER
from server.services.cron.daily_tasks import run_daily_tasks
from server.services.cron.search_index_task import refresh_search_index
from server.services.redis_client import check_rate_limit_setup
from server.services.security.api_key_auth import check_api_key_setup
from server.utils.brazil_datetime import BrazilDatetime


async def periodic_cache_cleanup() -> None:
    """Task que roda a cada 60 minutos limpando cache expirado"""
    while True:
        await asyncio.sleep(3600)
        count = clear_expired_cache()
        print(f"Cache cleanup: removed {count} expired entries")


async def periodic_daily_tasks() -> None:
    """Task que roda uma vez por dia, à meia-noite (horário de Brasília)"""
    while True:
        now = BrazilDatetime.now_utc()
        next_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        await asyncio.sleep((next_midnight - now).total_seconds())
        # In a thread: the tasks hit the DB and SMTP, which would otherwise
        # block the event loop (and every request) while they run.
        await asyncio.to_thread(run_daily_tasks)
        print("Daily tasks ran")


async def periodic_search_index_refresh() -> None:
    """Task que reconstrói o índice da busca pública a cada
    SEARCH_INDEX_REFRESH_SECONDS (padrão: 10 minutos)"""
    while True:
        await asyncio.sleep(CONFIG.search_index_refresh_seconds)
        # In a thread: REFRESH MATERIALIZED VIEW is a blocking DB call.
        await asyncio.to_thread(refresh_search_index)


async def cancel_task(task: asyncio.Task[None] | None) -> None:
    if task is None:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação"""
    print(await check_rate_limit_setup())
    print(check_api_key_setup())
    cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    print("Cache cleanup started")
    daily_tasks_task = asyncio.create_task(periodic_daily_tasks())
    print("Daily tasks scheduler started")
    search_index_task = asyncio.create_task(periodic_search_index_refresh())
    print("Search index refresh scheduler started")
    access_log_task = asyncio.create_task(
        ACCESS_LOG_WRITER.run_periodic_flush(CONFIG.access_log_flush_seconds)
    )
    print("API access log writer started")

    yield

    # Stopped first and flushed once more, so error rows from the last
    # requests are not lost on shutdown or restart.
    await cancel_task(access_log_task)
    await ACCESS_LOG_WRITER.flush(final=True)
    print("API access log writer stoped")

    await cancel_task(cleanup_task)
    print("Cache cleanup stoped")

    await cancel_task(daily_tasks_task)
    print("Daily tasks scheduler stoped")

    await cancel_task(search_index_task)
    print("Search index refresh scheduler stoped")
