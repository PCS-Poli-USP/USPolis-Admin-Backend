import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI

from server.cache import clear_expired_cache
from server.services.cron.daily_tasks import run_daily_tasks
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
        run_daily_tasks()
        print("Daily tasks ran")


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
    cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    print("Cache cleanup started")
    daily_tasks_task = asyncio.create_task(periodic_daily_tasks())
    print("Daily tasks scheduler started")

    yield

    await cancel_task(cleanup_task)
    print("Cache cleanup stoped")

    await cancel_task(daily_tasks_task)
    print("Daily tasks scheduler stoped")
