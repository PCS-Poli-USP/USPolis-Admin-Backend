import re

from bs4 import BeautifulSoup
from httpx import AsyncClient

from server.services.jupiter_crawler.curriculum_crawler.models import (
    CurriculumGeneralInfo,
    CurriculumSubjectInfo,
)

BASE_URL = "https://uspdigital.usp.br/jupiterweb/listarGradeCurricular?codcg=3"


class JupiterCurriculumCrawler:
    def __init__(self, codcur: int, codhab: int):
        self.__codcur: int = codcur
        self.__codhab: int = codhab
        self.__soup: BeautifulSoup

    async def crawl_curriculum(
        self, page_content: bytes | None = None
    ) -> tuple[
        CurriculumGeneralInfo,
        list[CurriculumSubjectInfo],
        list[CurriculumSubjectInfo],
        list[CurriculumSubjectInfo],
    ]:
        if page_content is None:
            page_content = await self.request_html()

        self.__soup = self.__build_soup(page_content)

        general_info = self.__extract_general_info()

        mandatory_subjects, free_subjects, elective_subjects = (
            self.__extract_all_subjects_by_category()
        )

        return general_info, mandatory_subjects, free_subjects, elective_subjects

    async def request_html(self) -> bytes:
        url = f"{BASE_URL}&codcur={self.__codcur}&codhab={self.__codhab}&tipo=N"
        async with AsyncClient() as client:
            page = await client.get(url)
            return page.content

    def __build_soup(self, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, "html.parser")

    # ============================================================
    # GENERAL INFO
    # ============================================================
    def __extract_general_info(self) -> CurriculumGeneralInfo:
        course_name = self.__get_final_course_name()
        minimal_duration, ideal_duration, maximal_duration = self.__get_durations()
        aac, aex = self.__get_aac_aex()
        specific_info_text = self.__get_specific_info_text()

        return CurriculumGeneralInfo(
            course_name=course_name,
            minimal_duration=minimal_duration,
            ideal_duration=ideal_duration,
            maximal_duration=maximal_duration,
            AAC=aac,
            AEX=aex,
            habilitation_number=self.__codhab,
            specific_info_text=specific_info_text,
        )

    def __get_final_course_name(self) -> str:
        text = self.__soup.get_text(" ", strip=True)

        hab_match = re.search(
            r"Habilitação:\s*(.*?)(\s+Observações:|\s+Informações Básicas|\s+Informa|$)",
            text,
        )
        if hab_match:
            return hab_match.group(1).strip()

        course_match = re.search(
            r"Curso:\s*(.*?)(\s+Habilitação:|\s+Observações:|\s+Informações Básicas|\s+Informa|$)",
            text,
        )
        if course_match:
            return course_match.group(1).strip()

        return "UNKNOWN"

    def __get_durations(self) -> tuple[int, int, int]:
        text = self.__soup.get_text(" ", strip=True)

        ideal_match = re.search(r"Ideal\s*([0-9]+)\s*semestres", text)
        min_match = re.search(r"Mínima\s*([0-9]+)\s*semestres", text)
        max_match = re.search(r"Máxima\s*([0-9]+)\s*semestres", text)

        ideal = int(ideal_match.group(1)) if ideal_match else 0
        minimum = int(min_match.group(1)) if min_match else 0
        maximum = int(max_match.group(1)) if max_match else 0

        return minimum, ideal, maximum

    def __get_aac_aex(self) -> tuple[int, int]:
        table = self.__soup.find("table", attrs={"id": "tabelaCargaHoraria"})
        if table is None:
            return 0, 0

        text = table.get_text(" ", strip=True)

        aac_match = re.search(r"AAC:\s*([0-9]+)", text)

        # pega o valor de "Total geral de carga horária exigida em extensão"
        aex_match = re.search(
            r"Total\s+geral\s+de\s+carga\s+hor[áa�]ria\s+exigida\s+em\s+extens[ãa�]o:\s*([0-9]+)",
            text,
            re.IGNORECASE,
        )

        aac = int(aac_match.group(1)) if aac_match else 0
        aex = int(aex_match.group(1)) if aex_match else 0

        return aac, aex

    def __get_specific_info_text(self) -> str:
        """
        Pega o texto inteiro da tabela que contém "Informações Específicas",
        mesmo com encoding quebrado.
        """
        target_table = None

        for b in self.__soup.find_all("b"):
            b_text = b.get_text(" ", strip=True)

            if "Informa" in b_text and "Espec" in b_text:
                target_table = b.find_parent("table")
                break

        if target_table is None:
            return ""

        text = target_table.get_text("\n", strip=True)

        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()

    # ============================================================
    # SUBJECTS
    # ============================================================
    def __is_valid_subject_code(self, code: str) -> bool:
        valid_alpha = re.match(r"^[A-Z]{3}[0-9]{4}$", code)
        valid_numeric = re.match(r"^[0-9]{7}$", code)
        return bool(valid_alpha or valid_numeric)

    def __normalize_subject_code(self, code: str) -> str:
        return re.sub(r"\s+", "", code).strip()

    def __extract_all_subjects_by_category(
        self,
    ) -> tuple[
        list[CurriculumSubjectInfo],
        list[CurriculumSubjectInfo],
        list[CurriculumSubjectInfo],
    ]:
        mandatory: list[CurriculumSubjectInfo] = []
        free: list[CurriculumSubjectInfo] = []
        elective: list[CurriculumSubjectInfo] = []

        rows = self.__soup.find_all("tr")

        current_section: str | None = None
        current_period = 0

        for row in rows:
            # detecta título da seção pelo <b>
            b = row.find("b")
            if b is not None:
                title = b.get_text(" ", strip=True)

                if "Disciplinas" in title and "Obrigat" in title:
                    current_section = "mandatory"
                    continue

                if "Disciplinas" in title and "Optativas" in title and "Livres" in title:
                    current_section = "free"
                    continue

                if "Disciplinas" in title and "Optativas" in title and "Eletivas" in title:
                    current_section = "elective"
                    continue

            if current_section is None:
                continue

            row_text = row.get_text(" ", strip=True)

            # detecta período ideal (mesmo quebrado)
            period_match = re.search(r"([0-9]+)[ºo�]?\s*Per", row_text)
            if period_match:
                current_period = int(period_match.group(1))

            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            subject_code = cols[0].get_text(strip=True)
            subject_name = cols[1].get_text(strip=True)

            subject_code = self.__normalize_subject_code(subject_code)

            if not self.__is_valid_subject_code(subject_code):
                continue

            subj = CurriculumSubjectInfo(
                subject_code=subject_code,
                subject_name=subject_name.strip(),
                period=current_period,
            )

            if current_section == "mandatory":
                mandatory.append(subj)
            elif current_section == "free":
                free.append(subj)
            elif current_section == "elective":
                elective.append(subj)

        def unique_list(items: list[CurriculumSubjectInfo]) -> list[CurriculumSubjectInfo]:
            unique = {}
            for s in items:
                unique[s.subject_code] = s
            return list(unique.values())

        return unique_list(mandatory), unique_list(free), unique_list(elective)