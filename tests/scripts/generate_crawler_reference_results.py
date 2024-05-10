import asyncio

from tests.services.jupiter_crawler.crawler_test_utils import JupiterCrawlerTestUtils

asyncio.run(JupiterCrawlerTestUtils.create_reference_results())
