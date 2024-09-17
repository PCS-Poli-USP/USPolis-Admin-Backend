# Lógicas consideradas :
#
# datas de activation e deactivation de um Subject sao as de
# inicio e fim da sua primeira Class
#

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from httpx import AsyncClient

from server.models.database.calendar_db_model import Calendar
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.services.jupiter_crawler.models import (
    GeneralInfo,
    ScheduleInfo,
    StudentNumbersInfo,
)
from server.utils.enums.class_type import ClassType
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.subject_type import SubjectType
from server.utils.enums.week_day import WeekDay
from server.utils.time_utils import TimeUtils

BASE_URL = "https://uspdigital.usp.br/jupiterweb/obterTurma?nomdis=&sgldis="
CLASS_DIV_IDENTIFIERS = {
    "style": "border: 2px solid #658CCF; padding: 5px; border-radius: 5px;"
}


class JupiterCrawler:
    def __init__(self, subject_code: str):
        self.__subject_code: str
        self.__soup: BeautifulSoup
        self.__subject_professors: set[str] = set()
        self.__subject_code = subject_code

    @staticmethod
    async def crawl_subject_static(
        subject_code: str,
        calendars: list[Calendar] = [],
        page_content: bytes | None = None,
    ) -> Subject:
        crawler = JupiterCrawler(subject_code)
        return await crawler.crawl_subject(calendars, page_content)

    async def crawl_subject(
        self, calendars: list[Calendar] = [], page_content: bytes | None = None
    ) -> Subject:
        if page_content is None:
            page_content = await self.request_html()
        self.__soup = self.__build_soap(page_content)
        crawled_classes = self.__extract_classes_info()
        for class_ in crawled_classes:
            class_.calendars = calendars

        subject = Subject(
            code=self.__subject_code,
            name=self.__get_subject_name(),
            classes=crawled_classes,
            # TODO: checar se disc. quadrimestral difere em algo no jupiter
            type=SubjectType.BIANNUAL,
            professors=sorted(list(self.__subject_professors)),
            class_credit=0,
            work_credit=0,
            activation=crawled_classes[0].start_date,
            deactivation=crawled_classes[0].end_date,
        )
        return subject

    async def request_html(self) -> bytes:
        async with AsyncClient() as client:
            page = await client.get(BASE_URL + self.__subject_code)
            return page.content

    def __build_soap(self, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, "html.parser")

    def __get_subject_name(self) -> Any:
        subject = self.__soup.find_all("b", text=re.compile("Disciplina:(.*)"))[0]
        return subject.get_text().replace(f"Disciplina: {self.__subject_code} - ", "")

    def __extract_classes_info(self) -> list[Class]:
        classes_soups = self.__soup.find_all("div", attrs=CLASS_DIV_IDENTIFIERS)
        classes: list[Class] = []
        for index, class_soup in enumerate(classes_soups):
            try:
                class_professors_set: set[str] = set()
                tables = class_soup.find_all("table")
                if len(tables) == 4:
                    tables.pop(2)
                if len(tables) != 3:
                    raise Exception("Not valid class format")
                general_info_table_rows = tables[0].find_all("tr")
                schedules_table_rows = tables[1].find_all("tr")
                student_numbers_table_rows = tables[2].find_all("tr")

                general_info = self.__get_general_info(general_info_table_rows)
                schedules_infos = self.__get_schedules_infos(schedules_table_rows)
                student_numbers_info = self.__get_student_numbers_info(
                    student_numbers_table_rows
                )

                class_ = Class(
                    start_date=general_info.start_date,
                    end_date=general_info.end_date,
                    code=general_info.class_code,
                    type=general_info.class_type,
                    vacancies=student_numbers_info.vacancies,
                    subscribers=student_numbers_info.subscribers,
                    pendings=student_numbers_info.pendings,
                    professors=[],
                    schedules=[],
                )
                for schedule_info in schedules_infos:
                    schedule = Schedule(
                        start_date=general_info.start_date,
                        end_date=general_info.end_date,
                        week_day=schedule_info.week_day,
                        start_time=schedule_info.start_time,
                        end_time=schedule_info.end_time,
                        recurrence=Recurrence.WEEKLY,
                    )

                    class_.schedules.append(schedule)
                    class_professors_set.update(schedule_info.professors)
                    self.__subject_professors.update(schedule_info.professors)

                class_.professors = sorted(list(class_professors_set))
                classes.append(class_)
            except Exception as e:
                print(
                    f"Ignoring exception trying to crawl {
                        index}th class on {self.__subject_code} subject:\n",
                    e,
                )

        return classes

    def __get_general_info(self, rows: Any) -> GeneralInfo:
        class_code: str = rows[0].find_all("td")[1].get_text(strip=True)
        start_period: str = rows[1].find_all("td")[1].get_text(strip=True)
        end_period: str = rows[2].find_all("td")[1].get_text(strip=True)
        class_type: str = rows[3].find_all("td")[1].get_text(strip=True)
        try:
            obs = rows[4].find_all("td")[1].get_text(strip=True)
        except IndexError:
            obs = ""

        return GeneralInfo(
            class_code=class_code,
            start_date=datetime.strptime(start_period, "%d/%m/%Y"),
            end_date=datetime.strptime(end_period, "%d/%m/%Y"),
            class_type=ClassType.from_str(class_type),
            obs=obs,
        )

    def __get_schedules_infos(self, rows: Any) -> list[ScheduleInfo]:
        schedules_infos: list[ScheduleInfo] = []
        rows_dropped = rows[1:]
        for row in rows_dropped:
            data = row.find_all("td")

            week_day: str = data[0].get_text(strip=True)
            start_time: str = data[1].get_text(strip=True)
            end_time: str = data[2].get_text(strip=True)
            professor: str = data[3].get_text(strip=True)

            # More than one professor - only the first row has info, the others only have
            # the additional professor
            if (
                week_day == ""
                and start_time == ""
                and end_time == ""
                and professor != ""
            ):
                previous_schedule_info = schedules_infos[len(schedules_infos) - 1]
                previous_schedule_info.professors.append(professor)
                previous_schedule_info.professors = sorted(
                    previous_schedule_info.professors
                )
                continue

            # More than one hour in same day - only week day is empty
            if (
                week_day == ""
                and start_time != ""
                and end_time != ""
                and professor != ""
            ):
                previous_schedule_info = schedules_infos[len(schedules_infos) - 1]
                week_day_as_enum = previous_schedule_info.week_day
            else:
                week_day_as_enum = WeekDay.from_str(week_day)

            schedules_infos.append(
                ScheduleInfo(
                    week_day=week_day_as_enum,
                    professors=[professor],
                    start_time=TimeUtils.time_from_string(start_time),
                    end_time=TimeUtils.time_from_string(end_time),
                )
            )
        return schedules_infos

    def __get_student_numbers_info(self, rows: Any) -> StudentNumbersInfo:
        student_numbers_info = StudentNumbersInfo(
            vacancies=0, subscribers=0, pendings=0, enrolled=0
        )

        # drop the first row, which is the header
        rows_dropped = rows[1:]

        filter = {"class": "txt_arial_8pt_black"}
        for row in rows_dropped:
            data = row.find_all("span", attrs=filter)

            # The filter is of black text. If the data is empty, it means that the text on
            # the row is not black, so it should be ignored
            if data == []:
                continue

            if len(data) == 6:
                # drop the first column, which is an empty one
                data.pop(0)

            vacancies_text = data[1].get_text(strip=True)
            subscribers_text = data[2].get_text(strip=True)
            pendings_text = data[3].get_text(strip=True)
            enrolled_text = data[4].get_text(strip=True)

            if vacancies_text != "" and vacancies_text.isdigit():
                student_numbers_info.vacancies += int(vacancies_text)
            if subscribers_text != "" and subscribers_text.isdigit():
                student_numbers_info.subscribers += int(subscribers_text)
            if pendings_text != "" and pendings_text.isdigit():
                student_numbers_info.pendings += int(pendings_text)
            if enrolled_text != "" and enrolled_text.isdigit():
                student_numbers_info.enrolled += int(enrolled_text)

        return student_numbers_info


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        import json

        subject_code = "PEA3311"
        crawler = JupiterCrawler(subject_code)
        subject = await crawler.crawl_subject()
        print(json.dumps(json.loads(subject.model_dump_json()), indent=4))

    asyncio.run(main())
