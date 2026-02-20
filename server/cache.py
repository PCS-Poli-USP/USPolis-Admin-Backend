from datetime import datetime, timedelta, date
from functools import wraps
from typing import Any, TypeVar
from collections.abc import Callable
import inspect

from pydantic import BaseModel

from server.utils.brazil_datetime import BrazilDatetime

# Cache em memória
_cache_store: dict[str, tuple[Any, datetime]] = {}
_expired_map: dict[str, int] = {}

T = TypeVar("T")


def simple_cache(
    expire_seconds: int = 600,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache que funciona com funções sync e async"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache_key = f"cache:{func.__name__}"
        _expired_map[cache_key] = expire_seconds
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                if cache_key in _cache_store:
                    cached_data, cached_time = _cache_store[cache_key]
                    if BrazilDatetime.now_utc() - cached_time < timedelta(
                        seconds=expire_seconds
                    ):
                        return cached_data  # type: ignore
                    else:
                        del _cache_store[cache_key]

                result = await func(*args, **kwargs)
                _cache_store[cache_key] = (result, BrazilDatetime.now_utc())
                return result  # type: ignore

            return async_wrapper  # type: ignore
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                if cache_key in _cache_store:
                    cached_data, cached_time = _cache_store[cache_key]
                    if BrazilDatetime.now_utc() - cached_time < timedelta(
                        seconds=expire_seconds
                    ):
                        return cached_data  # type: ignore
                    else:
                        del _cache_store[cache_key]

                result = func(*args, **kwargs)
                _cache_store[cache_key] = (result, BrazilDatetime.now_utc())
                return result

            return sync_wrapper

    return decorator


def date_range_cache(
    expire_seconds: int = 600,
    interval_param: str | None = None,
    start_param: str = "start",
    end_param: str = "end",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache para rotas com datas que funciona com sync e async"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                start_date: datetime | None = None
                end_date: datetime | None = None

                if interval_param:
                    interval: Any = kwargs.get(interval_param)
                    if (
                        interval
                        and hasattr(interval, "start")
                        and hasattr(interval, "end")
                    ):
                        if interval.start and interval.end:
                            start_date = datetime.combine(
                                interval.start, datetime.min.time()
                            )
                            end_date = datetime.combine(
                                interval.end, datetime.min.time()
                            )
                else:
                    start: date | None = kwargs.get(start_param)
                    end: date | None = kwargs.get(end_param)
                    if start and end:
                        start_date = datetime.combine(start, datetime.min.time())
                        end_date = datetime.combine(end, datetime.min.time())

                if start_date and end_date:
                    today = BrazilDatetime.now_utc()
                    cache_start = today - timedelta(days=15)
                    cache_end = today + timedelta(days=15)

                    if start_date >= cache_start and end_date <= cache_end:
                        cache_key = f"cache:{func.__name__}:{cache_start.date()}:{cache_end.date()}"
                        _expired_map[cache_key] = expire_seconds

                        if cache_key in _cache_store:
                            cached_data, cached_time = _cache_store[cache_key]
                            if BrazilDatetime.now_utc() - cached_time < timedelta(
                                seconds=expire_seconds
                            ):
                                return cached_data  # type: ignore
                            else:
                                del _cache_store[cache_key]

                        result = await func(*args, **kwargs)
                        _cache_store[cache_key] = (result, BrazilDatetime.now_utc())
                        return result  # type: ignore

                return await func(*args, **kwargs)  # type: ignore

            return async_wrapper  # type: ignore
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                start_date: datetime | None = None
                end_date: datetime | None = None

                if interval_param:
                    interval: Any = kwargs.get(interval_param)
                    if (
                        interval
                        and hasattr(interval, "start")
                        and hasattr(interval, "end")
                    ):
                        if interval.start and interval.end:
                            start_date = datetime.combine(
                                interval.start, datetime.min.time()
                            )
                            end_date = datetime.combine(
                                interval.end, datetime.min.time()
                            )
                else:
                    start: date | None = kwargs.get(start_param)
                    end: date | None = kwargs.get(end_param)
                    if start and end:
                        start_date = datetime.combine(start, datetime.min.time())
                        end_date = datetime.combine(end, datetime.min.time())

                if start_date and end_date:
                    today = BrazilDatetime.now_utc()
                    cache_start = today - timedelta(days=15)
                    cache_end = today + timedelta(days=15)

                    if start_date >= cache_start and end_date <= cache_end:
                        cache_key = f"cache:{func.__name__}:{cache_start.date()}:{cache_end.date()}"
                        _expired_map[cache_key] = expire_seconds
                        if cache_key in _cache_store:
                            cached_data, cached_time = _cache_store[cache_key]
                            if BrazilDatetime.now_utc() - cached_time < timedelta(
                                seconds=expire_seconds
                            ):
                                return cached_data  # type: ignore
                            else:
                                del _cache_store[cache_key]

                        result = func(*args, **kwargs)
                        _cache_store[cache_key] = (result, BrazilDatetime.now_utc())
                        return result

                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


def clear_cache() -> int:
    """Clear all cache entries and return the number of cleared entries"""
    count = len(_cache_store)
    _cache_store.clear()
    return count


def clear_expired_cache() -> int:
    """Clear only expired cache entries and return the number of cleared entries"""
    now = BrazilDatetime.now_utc()
    expired_keys = [
        key
        for key, (_, cached_time) in _cache_store.items()
        if now - cached_time > timedelta(seconds=_expired_map.get(key, 3600))
    ]
    for key in expired_keys:
        del _cache_store[key]
    return len(expired_keys)


class CacheKeyInfo(BaseModel):
    key: str
    age_seconds: int
    expired: bool


class CacheStats(BaseModel):
    total_keys: int
    keys: list[CacheKeyInfo]


def get_cache_stats() -> CacheStats:
    """Return stats about the current cache entries, including age and expiration status"""
    now = BrazilDatetime.now_utc()
    stats = CacheStats(total_keys=len(_cache_store), keys=[])

    for key, (_, cached_time) in _cache_store.items():
        age = (now - cached_time).total_seconds()
        stats.keys.append(
            CacheKeyInfo(
                key=key,
                age_seconds=int(age),
                expired=age > _expired_map.get(key, 3600),
            )
        )

    return stats
