from dataclasses import dataclass
from datetime import time
from pathlib import Path
import os

from playwright.async_api import Locator, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from server.services.jupiter_crawler.models import (
    JupiterScheduleSlot,
    JupiterStudentSchedule,
    JupiterStudentSubject,
)
from server.utils.enums.week_day import WeekDay
from server.utils.time_utils import TimeUtils

LOGIN_URL = "https://uspdigital.usp.br/jupiterweb/webLogin.jsp"
USER_INFO_URL = (
    "https://uspdigital.usp.br/jupiterweb/uspDadosPessoaisMostrar?codmnu=4543"
)
WEEK_DAYS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
MAX_RETRIES = 10

REPO_ROOT = Path(__file__).resolve().parents[3]
os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH", str(REPO_ROOT / ".playwright-browsers")
)


class JupiterAuthenticationError(Exception):
    pass


@dataclass
class _SubjectAccumulator:
    name: str
    class_code: str
    observations: str
    slots: list[JupiterScheduleSlot]


class AuthenticatedJupiterCrawler:
    @staticmethod
    async def crawl_student_schedule_static(
        n_usp: str,
        password: str,
        retry: int = 0,
    ) -> JupiterStudentSchedule:
        crawler = AuthenticatedJupiterCrawler()
        return await crawler.crawl_student_schedule(n_usp, password, retry)

    async def crawl_student_schedule(
        self,
        n_usp: str,
        password: str,
        retry: int = 0,
    ) -> JupiterStudentSchedule:
        if retry >= MAX_RETRIES:
            raise RuntimeError("Max retries reached while scraping JupiterWeb")

        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=["--no-sandbox"],
                )
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/69.0.3497.100 Safari/537.36"
                    )
                )
                page = await context.new_page()

                await page.goto(LOGIN_URL, timeout=15000)
                await page.locator("input[name='codpes']").fill(n_usp)
                await page.locator("input[name='senusu']").fill(password)
                await page.keyboard.press("Enter")

                try:
                    await page.wait_for_selector(
                        "a[href='gradeHoraria?codmnu=4759']",
                        timeout=5000,
                    )
                except PlaywrightTimeoutError as exc:
                    raise JupiterAuthenticationError(
                        "Erro ao acessar o JupiterWeb. Cheque suas credenciais."
                    ) from exc

                await page.click("a[href='gradeHoraria?codmnu=4759']")
                await page.wait_for_selector("#codpgm", timeout=15000)

                options = await self._get_program_options(page)
                if not options:
                    raise RuntimeError("Nenhum programa disponível para seleção no JupiterWeb")

                selected_option = sorted(options, key=int)[-1]
                await page.select_option("#codpgm", value=selected_option)
                await page.click("#buscar")

                # Some terms return no classes or use non-sequential row ids.
                # We only need to wait for the grade page to settle before parsing.
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except PlaywrightTimeoutError:
                    pass

                await self._wait_for_grade_content(page)

                course_raw = await page.locator("#curso").text_content() or ""
                institute_raw = await page.locator("#unidade").text_content() or ""
                course = self._extract_course_name(course_raw)
                institute = self._extract_institute_name(institute_raw)

                subjects_map = await self._extract_subjects(page)

                await page.goto(USER_INFO_URL, wait_until="load")

                fonts_texts: list[str | None] = await page.eval_on_selector_all(
                    "font",
                    "(elements) => elements.map((el) => el.textContent)",
                )
                personal_texts: list[str | None] = await page.eval_on_selector_all(
                    "td[width='77%'] font",
                    "(elements) => elements.map((el) => el.textContent)",
                )

                name = self._clean(personal_texts[1]) if len(personal_texts) > 1 else ""
                name = name or "Estudante USP"

                emails = [
                    self._clean(text) for text in fonts_texts if text and "@" in text
                ]
                preferred_email = next(
                    (email for email in emails if "usp.br" in email), ""
                )
                email = preferred_email or (emails[0] if emails else n_usp)

                subjects = [
                    JupiterStudentSubject(
                        code=code,
                        name=acc.name,
                        class_code=acc.class_code,
                        available_days=acc.slots,
                        observations=acc.observations,
                    )
                    for code, acc in sorted(subjects_map.items())
                ]

                await context.close()
                await browser.close()

                return JupiterStudentSchedule(
                    n_usp=n_usp,
                    name=name,
                    email=email,
                    course=course,
                    institute=institute,
                    subjects=subjects,
                )
        except Exception as exc:
            if "Failed to launch" in str(exc):
                return await self.crawl_student_schedule(n_usp, password, retry + 1)
            raise

    async def _extract_subjects(self, page: Page) -> dict[str, _SubjectAccumulator]:
        subjects: dict[str, _SubjectAccumulator] = {}
        first_click = True

        row_ids: list[str] = await page.eval_on_selector_all(
            "tr[id]",
            """
            (rows) => rows
                .map((row) => row.getAttribute('id') || '')
                .filter((id) => /^\\d+$/.test(id))
            """,
        )

        if not row_ids:
            return subjects

        for row_id in sorted({int(value) for value in row_ids}):
            start_hour_text = await page.locator(
                f"tr[id='{row_id}'] > td:nth-child(1)"
            ).text_content()
            end_hour_text = await page.locator(
                f"tr[id='{row_id}'] > td:nth-child(2)"
            ).text_content()

            start_hour = self._parse_hour(start_hour_text)
            end_hour = self._parse_hour(end_hour_text)
            if start_hour is None or end_hour is None:
                continue

            for td_index in range(3, 9):
                subject_cell = page.locator(
                    f"tr[id='{row_id}'] > td:nth-child({td_index})"
                )
                cell_text = self._clean(await subject_cell.text_content())
                if not cell_text:
                    continue

                splited_text = cell_text.split("-")
                code_from_cell = splited_text[0].strip()
                class_code_from_cell = (
                    splited_text[1].strip() if len(splited_text) > 1 else ""
                )
                if not code_from_cell:
                    continue

                details = await self._open_subject_details(
                    page,
                    subject_cell,
                    code_from_cell,
                    first_click=first_click,
                )
                first_click = False

                subject_code = details["code"] or code_from_cell
                subject_name = details["name"] or subject_code
                class_code = class_code_from_cell or ""
                observations = details["observations"]

                slot = JupiterScheduleSlot(
                    week_day=WeekDay.from_str(WEEK_DAYS[td_index - 3]),
                    start_time=start_hour,
                    end_time=end_hour,
                )

                if subject_code not in subjects:
                    subjects[subject_code] = _SubjectAccumulator(
                        name=subject_name,
                        class_code=class_code,
                        observations=observations,
                        slots=[slot],
                    )
                else:
                    subjects[subject_code].slots.append(slot)
                    if observations and not subjects[subject_code].observations:
                        subjects[subject_code].observations = observations

        return subjects

    async def _open_subject_details(
        self,
        page: Page,
        subject_cell: Locator,
        subject_code: str,
        first_click: bool,
    ) -> dict[str, str]:
        trigger_candidates = subject_cell.locator("span, a, button")
        if await trigger_candidates.count() > 0:
            trigger = trigger_candidates.first
        else:
            trigger = subject_cell

        await trigger.click()
        await self._wait_overlay(page)

        # JupiterWeb sometimes ignores the first click in this popup.
        if first_click:
            await trigger.click()
            await self._wait_overlay(page)

        await page.click('a[href="#div_oferecimento"]')
        await self._wait_overlay(page)

        code = self._clean(await page.locator(".coddis").first.text_content())
        name = self._clean(await page.locator(".nomdis").first.text_content())
        observations = self._clean(
            await page.locator(
                'div.adicionado table tbody tr td[class="obstur"]'
            ).first.text_content()
        )

        return {
            "code": code,
            "name": name,
            "observations": observations,
        }

    async def _wait_overlay(self, page: Page) -> None:
        try:
            await page.wait_for_selector(".blockOverlay", state="hidden", timeout=3000)
        except PlaywrightTimeoutError:
            # Overlay does not always show up.
            pass

    async def _wait_for_grade_content(self, page: Page) -> None:
        # The grade page often renders metadata spans before they receive content.
        # Consider the page ready when either metadata has text or schedule rows exist.
        try:
            await page.wait_for_function(
                """
                () => {
                    const curso = (document.querySelector('#curso')?.textContent || '').trim();
                    const unidade = (document.querySelector('#unidade')?.textContent || '').trim();
                    const rows = document.querySelectorAll("tr[id]").length;
                    return Boolean(curso || unidade || rows > 0);
                }
                """,
                timeout=15000,
            )
        except PlaywrightTimeoutError:
            # If no content appears we still proceed and return what is available.
            pass

    async def _get_program_options(self, page: Page) -> list[str]:
        # The select can render first with only the empty placeholder option.
        try:
            await page.wait_for_function(
                """
                () => {
                    const options = document.querySelectorAll('#codpgm option');
                    return Array.from(options).some((option) => {
                        const value = (option.getAttribute('value') || '').trim();
                        return value !== '';
                    });
                }
                """,
                timeout=10000,
            )
        except PlaywrightTimeoutError:
            pass

        values: list[str | None] = await page.eval_on_selector_all(
            "#codpgm option",
            "(options) => options.map((option) => option.getAttribute('value'))",
        )

        return [
            value.strip()
            for value in values
            if value is not None and value.strip() != ""
        ]

    @staticmethod
    def _extract_course_name(course_text: str) -> str:
        chunks = [chunk.strip() for chunk in course_text.split(" - ") if chunk.strip()]
        for chunk in chunks:
            if not chunk.isdigit():
                return chunk
        return chunks[-1] if chunks else ""

    @staticmethod
    def _extract_institute_name(institute_text: str) -> str:
        chunks = [
            chunk.strip() for chunk in institute_text.split(" - ") if chunk.strip()
        ]
        return chunks[1] if len(chunks) > 1 else (chunks[0] if chunks else "")

    @staticmethod
    def _parse_hour(hour_text: str | None) -> time | None:
        if not hour_text:
            return None
        hour_clean = hour_text.strip()
        if not hour_clean:
            return None
        return TimeUtils.time_from_string(hour_clean)

    @staticmethod
    def _clean(value: str | None) -> str:
        return (value or "").replace("\n", " ").strip()
