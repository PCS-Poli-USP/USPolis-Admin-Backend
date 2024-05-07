import json

import pytest

from server.services.jupiter_crawler.crawler import JupiterCrawler
from tests.services.jupiter_crawler.utils import JupiterCrawlerTestUtils


@pytest.mark.skip(reason="This test is not ready yet")
async def test_crawler(subject_code: str) -> None:
    reference_result = JupiterCrawlerTestUtils.retrieve_reference_results()[subject_code]
    page_contents = JupiterCrawlerTestUtils.retrieve_html_contents()
    result = await JupiterCrawler.crawl_subject_static(
        subject_code, page_contents[subject_code]
    )

    result_json: dict = json.loads(result.model_dump_json())
    reference_result_json: dict = json.loads(reference_result.model_dump_json())

    assert result_json == reference_result_json

test_cases = JupiterCrawlerTestUtils.retrieve_subject_codes_to_test()

@pytest.mark.parametrize("subject_code", test_cases)
def test_crawler_parametrized(subject_code: str) -> None:
    pytest.mark.asyncio(test_crawler(subject_code))

