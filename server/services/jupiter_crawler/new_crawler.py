import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup, ResultSet

BASE_URL = "https://uspdigital.usp.br/jupiterweb/obterTurma?nomdis=&sgldis="
CLASS_DIV_IDENTIFIERS = {
    "style": "border: 2px solid #658CCF; padding: 5px; border-radius: 5px;"
}


class JupiterCrawler:
    _subject_code: str
    _soup: BeautifulSoup
    _classes_divs: ResultSet

    @staticmethod
    def crawl_subject_static(subject_code: str) -> CrawledSubject:
        crawler = JupiterCrawler()
        return crawler.crawl_subject(subject_code)

    def crawl_subject(self, subject_code: str) -> CrawledSubject:
        self._subject_code = subject_code
