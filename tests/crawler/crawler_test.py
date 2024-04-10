import unittest
from src.common.crawler import JupiterCrawler
import json


class TestCrawler(unittest.TestCase):
    def setUp(self):
        with open("tests/crawler/test_results.json", "r") as f:
            self.test_results = json.load(f)

    def test_crawler(self):
        for input_str, expected_result in self.test_results.items():
            with self.subTest(input_str=input_str):
                try:
                    result = JupiterCrawler.crawl_subject_static(input_str)
                except Exception as e:
                    print(f"Eror while crawling {input_str}")
                    raise e

                self.assertEqual(len(result), len(expected_result))

                ignored_keys = [
                    "vacancies",
                    "subscribers",
                    "pendings",
                    "enrolled",
                ]
                for item1, item2 in zip(result, expected_result):
                    for key in ignored_keys:
                        if key in item1:
                            del item1[key]
                        if key in item2:
                            del item2[key]
                    self.assertEqual(item1, item2)

if __name__ == "__main__":
    unittest.main()
