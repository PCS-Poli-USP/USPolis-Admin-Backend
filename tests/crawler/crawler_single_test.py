import unittest
from src.common.crawler import JupiterCrawler
import json


class SingleTestCrawler(unittest.TestCase):
    SUBJECT = "PSI3211"

    def test_crawler(self):
        result = JupiterCrawler.crawl_subject_static(self.SUBJECT)
        with open("tests/crawler/single_test_result.json", "w") as f:
            json.dump({self.SUBJECT: result}, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
