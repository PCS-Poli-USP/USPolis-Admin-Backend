import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from httpx import AsyncClient

from server.services.jupiter_crawler.course_models import CourseOption


BASE_URL = "https://uspdigital.usp.br/jupiterweb/jupCursoLista"


class JupiterCoursesCrawler:
    def __init__(self, codcg: int, tipo: str = "N"):
        self.codcg = codcg
        self.tipo = tipo

    async def request_html(self) -> bytes:
        async with AsyncClient() as client:
            resp = await client.get(
                BASE_URL,
                params={"codcg": self.codcg, "tipo": self.tipo},
            )
            resp.raise_for_status()
            return resp.content

    def parse_courses(self, html: bytes) -> list[CourseOption]:
        soup = BeautifulSoup(html, "html.parser")

        results: list[CourseOption] = []

        links = soup.find_all("a", href=re.compile(r"listarGradeCurricular\?"))

        for a in links:
            href = a.get("href")
            if not href:
                continue

            parsed = urlparse(href)
            params = parse_qs(parsed.query)

            codcur = params.get("codcur", [None])[0]
            codhab = params.get("codhab", [None])[0]

            if codcur is None or codhab is None:
                continue

            course_name: Optional[str] = None
            row = a.find_parent("tr")

            if row:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    course_name = tds[1].get_text(strip=True)

            if course_name is None:
                course_name = ""

            results.append(
                CourseOption(
                    codcur=int(codcur),
                    codhab=int(codhab),
                    name=course_name,
                )
            )

        return results

    async def crawl(self) -> list[CourseOption]:
        html = await self.request_html()
        return self.parse_courses(html)