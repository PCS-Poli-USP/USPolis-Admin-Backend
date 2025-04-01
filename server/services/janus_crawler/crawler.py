from datetime import time
from bs4 import BeautifulSoup
from httpx import AsyncClient
import pandas as pd

from server.models.database.calendar_db_model import Calendar
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.services.janus_crawler.models import SubjectInfo
from server.utils.enums.class_type import ClassType
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.subject_type import SubjectType
from server.utils.enums.week_day import WeekDay

BASE_URL = "https://uspdigital.usp.br/janus/TurmaDet?sgldis="
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}
PARAMS = {"tipo": "T"}


class JanusCrawler:
    def __init__(self, subject_code: str):
        self.__subject_code: str
        self.__soup: BeautifulSoup
        self.__subject_code = subject_code

    @staticmethod
    async def crawl_subject_static(
        subject_code: str,
        calendars: list[Calendar] = [],
        page_content: bytes | None = None,
    ) -> Subject:
        crawler = JanusCrawler(subject_code)
        return await crawler.crawl_subject(calendars, page_content)

    async def __get_subject_ofe(self) -> str | None:
        """
        Get the subject offering code if subject code is valid or ofering exists.
        """
        async with AsyncClient() as client:
            response = await client.post(
                "https://uspdigital.usp.br/janus/DisciplinaAux",
                params=PARAMS,
                headers=HEADERS,
                data={"sgldis": self.__subject_code, "nomdis": ""},
            )
            for item in response.text.split('"'):
                if f"publico/turma/{self.__subject_code}/" in item:
                    return item.split("/")[-1]
            return None

    async def request_html(self, ofe: str) -> bytes:
        async with AsyncClient() as client:
            page = await client.get(
                f"{BASE_URL}{self.__subject_code}&ofe={ofe}&", headers=HEADERS
            )
            return page.content

    def __build_soap(self, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, "html.parser")

    def __get_subject_info(self) -> SubjectInfo:
        tables = self.__soup.find_all("table")
        df = pd.read_html(str(tables), flavor="bs4")[0]
        clean_df = df.dropna()

        professors_raw = df[0].iloc[17]
        if clean_df.shape[0] > 1:
            date_row = clean_df.iloc[1]
            start_time = date_row[1].split("-")[0].strip()
            end_time = date_row[1].split("-")[1].strip()
            day = date_row[0]
        else:
            date_row = None
            start_time = ""
            end_time = ""
            day = ""

        info = SubjectInfo(
            class_code=df[0].iloc[0].split("-")[1].strip(),
            subject_name=df[0].iloc[1],
            subject_code=df[0].iloc[1],
            total_students=int(df[2].iloc[9]),
            start_date=df[0].iloc[13].split(":")[1].strip(),
            end_date=df[0].iloc[13].split(":")[2].strip(),
            credits=int(df[0].iloc[15].split(":")[1].strip()),
            start_time=time(start_time) if start_time else None,
            end_time=time(end_time) if end_time else None,
            week_day=WeekDay.from_long_str(day) if day else None,
            professors=[],
        )

        professors_raw_str = ""
        if isinstance(professors_raw, str):
            professors_raw_str = professors_raw

        for row in df.iterrows():
            str_row = str(row[1].iloc[0])
            if str_row == "nan":
                continue
            if str_row in info.professors and str_row != professors_raw_str:
                info.professors += [row[1].iloc[0]]

        if len(info.professors) == 0 and professors_raw_str:
            info.professors = [professors_raw_str]

        return info

    def __get_subject_classes(self, data: SubjectInfo) -> list[Class]:
        if not data.week_day or not data.start_time or not data.end_time:
            return []
        class_ = Class(
            code=data.class_code,
            start_date=data.start_date,
            end_date=data.end_date,
            professors=data.professors,
            type=ClassType.THEORIC,
            vacancies=data.total_students,
            schedules=[],
        )
        schedule = Schedule(
            start_date=data.start_date,
            end_date=data.end_date,
            start_time=data.start_time,
            end_time=data.end_time,
            week_day=data.week_day,
            recurrence=Recurrence.WEEKLY,
        )
        schedule.class_ = class_
        class_.schedules.append(schedule)
        return [class_]

    async def crawl_subject(
        self, calendars: list[Calendar] = [], page_content: bytes | None = None
    ) -> Subject:
        if page_content is None:
            ofe = await self.__get_subject_ofe()
            if ofe is None:
                raise Exception("Invalid subject code or offering does not exist.")
            page_content = await self.request_html(ofe)

        self.__soup = self.__build_soap(page_content)
        data = self.__get_subject_info()

        classes = self.__get_subject_classes(data)
        for class_ in classes:
            class_.calendars = calendars

        subject = Subject(
            code=self.__subject_code,
            name=data.subject_name,
            professors=data.professors,
            type=SubjectType.FOUR_MONTHLY,
            class_credit=data.credits,
            work_credit=0,
            classes=classes,
        )
        return subject
