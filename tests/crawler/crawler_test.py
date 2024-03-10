import unittest
from src.common.crawler import JupiterCrawler
import json

class TestCrawler(unittest.TestCase):
    def setUp(self):
        with open('tests/crawler/test_results.json', 'r') as f:
            self.test_results = json.load(f)

    def test_crawler(self):
        for input_str, expected_result in self.test_results.items():
            with self.subTest(input_str=input_str):
                try:
                    result = JupiterCrawler.crawl_subject_static(input_str)
                except Exception as e:
                    print(f"Eror while crawling {input_str}")
                    raise e
                self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
