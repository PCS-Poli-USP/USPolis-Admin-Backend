import json

import pytest

from server.services.jupiter_crawler.crawler import JupiterCrawler
from tests.services.jupiter_crawler.crawler_test_utils import (
    JUPITER_DATA_DIR,
    ensure_fresh_snapshot,
    retrieve_html_for_semester,
    retrieve_reference_for_semester,
)

CURRENT_SEMESTER = ensure_fresh_snapshot()
_manifest = json.loads(
    (JUPITER_DATA_DIR / "snapshots" / CURRENT_SEMESTER / "manifest.json").read_text(
        encoding="utf-8"
    )
)
test_cases: list[str] = _manifest["subject_codes"]


@pytest.mark.asyncio
@pytest.mark.parametrize("subject_code", test_cases)
async def test_crawler_parametrized(subject_code: str) -> None:
    reference_result_json = retrieve_reference_for_semester(
        subject_code, CURRENT_SEMESTER
    )
    result_json = await _crawler(subject_code)
    assert result_json == reference_result_json


async def _crawler(subject_code: str) -> dict:
    page_content = retrieve_html_for_semester(subject_code, CURRENT_SEMESTER)
    result = await JupiterCrawler.crawl_subject_static(
        subject_code, page_content=page_content
    )
    result_json: dict = json.loads(result.model_dump_json())
    return result_json
