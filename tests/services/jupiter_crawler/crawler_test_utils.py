import pickle

from server.models.database.subject_db_model import Subject
from server.services.jupiter_crawler.crawler import JupiterCrawler


class JupiterCrawlerTestUtils:
    _test_cases_file_path = "tests/data/test_cases/crawler_test_cases.txt"
    _contents_file_path = "tests/data/results/crawler_html_contents"
    _reference_results_file_path = "tests/data/results/crawler_reference_results"

    @classmethod
    def retrieve_subject_codes_to_test(cls) -> list[str]:
        with open(cls._test_cases_file_path) as f:
            return [line.strip() for line in f.readlines()]

    @classmethod
    def retrieve_reference_results(cls) -> dict[str, Subject]:
        with open(cls._reference_results_file_path, "rb") as file:
            results: dict[str, Subject] = pickle.load(file)
            return results

    @classmethod
    def retrieve_html_contents(cls) -> dict[str, bytes]:
        with open(cls._contents_file_path, "rb") as file:
            contents_dict: dict[str, bytes] = pickle.load(file)
            return contents_dict

    @classmethod
    async def create_html_pages_data(cls) -> None:
        subject_codes_to_test = cls.retrieve_subject_codes_to_test()

        contents_dict: dict[str, bytes] = {}
        for subject_code in subject_codes_to_test:
            crawler = JupiterCrawler(subject_code)
            content = await crawler.request_html()
            contents_dict[subject_code] = content

        cls._save_html_contents(contents_dict)

    @classmethod
    async def create_reference_results(cls) -> None:
        results: dict[str, Subject] = {}

        contents_dict = cls.retrieve_html_contents()

        for subject_code, content in contents_dict.items():
            print(subject_code)
            try:
                results[subject_code] = await JupiterCrawler.crawl_subject_static(
                    subject_code=subject_code,
                    calendars=[],
                    page_content=content,
                )
            except Exception as e:
                print(f"Error processing {subject_code}: {e}")
                continue

        cls._save_reference_results(results)

    @classmethod
    def _save_html_contents(cls, contents: dict[str, bytes]) -> None:
        with open(cls._contents_file_path, "wb") as file:
            pickle.dump(contents, file)

    @classmethod
    def _save_reference_results(cls, results: dict[str, Subject]) -> None:
        with open(cls._reference_results_file_path, "wb") as file:
            pickle.dump(results, file)
