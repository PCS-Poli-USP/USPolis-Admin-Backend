import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from server.config import CONFIG
from server.services.jupiter_crawler.authenticated_crawler import (
    AuthenticatedJupiterCrawler,
)
from server.services.jupiter_crawler.crawl_limiter import (
    JupiterCrawlAlreadyRunning,
    JupiterCrawlerBusy,
    JupiterCrawlTimeout,
    crawl_slot,
)


@pytest.fixture(autouse=True)
def limiter_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(CONFIG, "jupiter_crawl_lock_dir", str(tmp_path))
    monkeypatch.setattr(CONFIG, "jupiter_crawl_max_concurrent", 2)
    monkeypatch.setattr(CONFIG, "jupiter_crawl_queue_seconds", 0.3)
    monkeypatch.setattr(CONFIG, "jupiter_crawl_timeout_seconds", 60)


class TestCrawlSlot:
    @pytest.mark.asyncio
    async def test_allows_up_to_the_configured_concurrency(self) -> None:
        async with crawl_slot("111"), crawl_slot("222"):
            pass

    @pytest.mark.asyncio
    async def test_rejects_when_all_slots_stay_taken(self) -> None:
        async with crawl_slot("111"), crawl_slot("222"):
            with pytest.raises(JupiterCrawlerBusy) as exc_info:
                async with crawl_slot("333"):
                    pass

        assert exc_info.value.status_code == 503
        assert exc_info.value.headers() == {"Retry-After": "30"}

    @pytest.mark.asyncio
    async def test_waits_for_a_slot_freed_within_the_queue_time(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(CONFIG, "jupiter_crawl_max_concurrent", 1)
        release = asyncio.Event()

        async def hold() -> None:
            async with crawl_slot("111"):
                await release.wait()

        holder = asyncio.create_task(hold())
        await asyncio.sleep(0.05)
        asyncio.get_running_loop().call_later(0.1, release.set)

        async with crawl_slot("222"):
            pass
        await holder

    @pytest.mark.asyncio
    async def test_rejects_a_second_crawl_for_the_same_account(self) -> None:
        async with crawl_slot("111"):
            with pytest.raises(JupiterCrawlAlreadyRunning) as exc_info:
                async with crawl_slot("111"):
                    pass

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_releases_everything_when_the_crawl_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(CONFIG, "jupiter_crawl_max_concurrent", 1)
        with pytest.raises(RuntimeError):
            async with crawl_slot("111"):
                raise RuntimeError("crawl failed")

        async with crawl_slot("111"):
            pass

    @pytest.mark.asyncio
    async def test_lock_files_do_not_name_the_account(self, tmp_path: Path) -> None:
        async with crawl_slot("12345678"):
            pass

        assert all("12345678" not in path.name for path in tmp_path.iterdir())


class TestCrawlStudentScheduleStatic:
    @pytest.mark.asyncio
    async def test_times_out_a_slow_crawl_and_frees_the_slot(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(CONFIG, "jupiter_crawl_timeout_seconds", 0.1)
        monkeypatch.setattr(CONFIG, "jupiter_crawl_max_concurrent", 1)

        async def slow_crawl(*args: object) -> None:
            await asyncio.sleep(5)

        with patch.object(
            AuthenticatedJupiterCrawler, "crawl_student_schedule", slow_crawl
        ):
            with pytest.raises(JupiterCrawlTimeout) as exc_info:
                await AuthenticatedJupiterCrawler.crawl_student_schedule_static(
                    "111", "pw"
                )

        assert exc_info.value.status_code == 504
        async with crawl_slot("111"):
            pass

    @pytest.mark.asyncio
    async def test_busy_host_never_starts_a_browser(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(CONFIG, "jupiter_crawl_max_concurrent", 1)
        crawl = AsyncMock()

        with patch.object(AuthenticatedJupiterCrawler, "crawl_student_schedule", crawl):
            async with crawl_slot("111"):
                with pytest.raises(JupiterCrawlerBusy):
                    await AuthenticatedJupiterCrawler.crawl_student_schedule_static(
                        "222", "pw"
                    )

        crawl.assert_not_called()
