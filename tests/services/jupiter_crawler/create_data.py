import asyncio
import pickle

from server.services.jupiter_crawler.crawler import JupiterCrawler


async def run() -> None:
    test_cases_file_path = "tests/services/jupiter_crawler/crawler_test_cases.txt"
    contents_file_path = "tests/services/jupiter_crawler/html_contents"

    with open(test_cases_file_path) as f:
        subject_codes_to_test = [line.strip() for line in f.readlines()]

    contents_dict: dict[str, bytes] = {}
    for subject_code in subject_codes_to_test:
        crawler = JupiterCrawler(subject_code)
        content = await crawler.request_html()
        contents_dict[subject_code] = content

    with open(contents_file_path, "wb") as file:
        pickle.dump(contents_dict, file)


if __name__ == "__main__":
    asyncio.run(run())
