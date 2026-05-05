import re
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from httpx import AsyncClient

from ..course_models import CourseOption


BASE_URL = "https://uspdigital.usp.br/jupiterweb/jupCursoLista"


class JupiterCoursesOldCrawler:
    def __init__(self, codcg: int, tipo: str = "V"):
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
        html_str = html.decode("windows-1252", errors="ignore")
        soup = BeautifulSoup(html_str, "html.parser")

        results: list[CourseOption] = []

        # pega todos os links que levam pra listarGradeCurricular
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

            # codcur também aparece no texto do link, mas vamos confiar mais na URL
            codcur_int = int(codcur)
            codhab_int = int(codhab)

            # pega a linha da tabela
            row = a.find_parent("tr")
            if not row:
                continue

            tds = row.find_all("td")
            if len(tds) < 3:
                continue

            nome_curso = tds[1].get_text(strip=True)
            habilitacao = tds[2].get_text(strip=True)

            # nome final (você pode ajustar isso)
            full_name = f"{nome_curso} - {habilitacao}"

            results.append(
                CourseOption(
                    codcur=codcur_int,
                    codhab=codhab_int,
                    name=full_name,
                )
            )

        return results

    async def crawl(self) -> list[CourseOption]:
        html = await self.request_html()
        return self.parse_courses(html)


if __name__ == "__main__":
    import asyncio
    import json

    async def main() -> None:
        crawler = JupiterCoursesOldCrawler(codcg=3, tipo="V")
        courses = await crawler.crawl()

        print(json.dumps([c.model_dump() for c in courses], indent=4, ensure_ascii=False))

    asyncio.run(main())