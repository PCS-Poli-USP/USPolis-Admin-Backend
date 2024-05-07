import json

import pytest

from server.services.jupiter_crawler.crawler import JupiterCrawler
from tests.services.jupiter_crawler.utils import JupiterCrawlerTestUtils


@pytest.mark.asyncio
async def test_crawler() -> None:
    subject_codes_to_test = JupiterCrawlerTestUtils.retrieve_subject_codes_to_test()
    reference_results = JupiterCrawlerTestUtils.retrieve_reference_results()
    page_contents = JupiterCrawlerTestUtils.retrieve_html_contents()

    for subject_code in subject_codes_to_test:
        reference_result = reference_results[subject_code]
        result = await JupiterCrawler.crawl_subject_static(
            subject_code, page_contents[subject_code]
        )

        result_json: dict = json.loads(result.model_dump_json())
        reference_result_json: dict = json.loads(reference_result.model_dump_json())

        assert result_json == reference_result_json
