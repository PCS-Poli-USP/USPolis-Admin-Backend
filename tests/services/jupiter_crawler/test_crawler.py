import json

import pytest

from server.services.jupiter_crawler.crawler import JupiterCrawler
from tests.services.jupiter_crawler.crawler_test_utils import JupiterCrawlerTestUtils

test_cases = JupiterCrawlerTestUtils.retrieve_subject_codes_to_test()

@pytest.mark.asyncio
@pytest.mark.parametrize("subject_code", test_cases)
async def test_crawler_parametrized(subject_code: str) -> None:
    reference_result = JupiterCrawlerTestUtils.retrieve_reference_results()[
        subject_code
    ]
    reference_result_json: dict = json.loads(reference_result.model_dump_json())
    result_json: dict = await _crawler(subject_code)
    assert result_json == reference_result_json


async def _crawler(subject_code: str) -> dict:
    page_contents = JupiterCrawlerTestUtils.retrieve_html_contents()
    result = await JupiterCrawler.crawl_subject_static(
        subject_code, page_contents[subject_code]
    )

    result_json: dict = json.loads(result.model_dump_json())
    return result_json
