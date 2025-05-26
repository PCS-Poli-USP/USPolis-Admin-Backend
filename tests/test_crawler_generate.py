from tests.services.jupiter_crawler.crawler_test_utils import JupiterCrawlerTestUtils


def test_crawler_generate_html_pages_data() -> None:
    """
    This test is used to generate the reference results for the crawler.
    It will create a file with the reference results in the data folder.
    """
    import asyncio

    from server.db import engine  # noqa

    asyncio.run(JupiterCrawlerTestUtils.create_html_pages_data())


def test_crawler_generate_reference_results() -> None:
    """
    This test is used to generate the reference results for the crawler.
    It will create a file with the reference results in the data folder.
    """
    import asyncio

    from server.db import engine  # noqa

    asyncio.run(JupiterCrawlerTestUtils.create_reference_results())
