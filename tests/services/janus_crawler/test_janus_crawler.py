import json

import pytest

from server.services.janus_crawler.crawler import JanusCrawler
from tests.services.crawler_snapshot_utils import snapshot_exists
from tests.services.janus_crawler.crawler_test_utils import (
    JANUS_SNAPSHOT_DIR,
    retrieve_html_for_code,
    retrieve_reference_for_code,
)

if not snapshot_exists(JANUS_SNAPSHOT_DIR):
    raise RuntimeError(
        f"No Janus crawler snapshot found at {JANUS_SNAPSHOT_DIR}. Janus isn't "
        "semester-scoped, so there's no automatic fetch here — run: poetry run "
        "python tests/scripts/generate_janus_snapshot.py"
    )

_manifest = json.loads(
    (JANUS_SNAPSHOT_DIR / "manifest.json").read_text(encoding="utf-8")
)
test_cases: list[str] = _manifest["subject_codes"]


@pytest.mark.asyncio
@pytest.mark.parametrize("subject_code", test_cases)
async def test_crawler_parametrized(subject_code: str) -> None:
    reference_result_json = retrieve_reference_for_code(subject_code)
    result_json = await _crawler(subject_code)
    assert result_json == reference_result_json


async def _crawler(subject_code: str) -> dict:
    page_content = retrieve_html_for_code(subject_code)
    result = await JanusCrawler.crawl_subject_static(
        subject_code, page_content=page_content
    )
    result_json: dict = json.loads(result.model_dump_json())
    return result_json
