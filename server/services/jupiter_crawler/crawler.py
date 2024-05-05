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
    subject_code: str
    url: str
    soup: BeautifulSoup
    subject_name: str
    classes_divs: ResultSet
    events: list

    def __reset(self) -> None:
        self.events = []

    @staticmethod
    def crawl_subject_static(subject_code: str) -> Any:
        crawler = JupiterCrawler()
        return crawler.crawl_subject(subject_code)

    def crawl_subject(self, subject_code: str) -> Any:
        self.subject_code = subject_code
        self.__reset()
        self.__build_url()
        self.__build_soap()
        self.__find_classes_divs()
        self.__extract_classes_info()
        self.__add_subject_info_to_events()
        return self.events

    def __build_url(self) -> Any:
        self.url = BASE_URL + self.subject_code

    def __build_soap(self) -> Any:
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.content, "html.parser")

    def __find_classes_divs(self) -> Any:
        self.classes_divs = self.soup.find_all("div", attrs=CLASS_DIV_IDENTIFIERS)

    def __extract_classes_info(self) -> Any:
        for class_div in self.classes_divs:
            result = self.__build_events_from_class_div(class_div)
            self.events += result

    def __build_events_from_class_div(self, class_div: Any) -> Any:
        result = []
        info_tables = class_div.find_all("table")
        if len(info_tables) == 4:
            info_tables.pop(2)
        if len(info_tables) != 3:
            return []
        general_info = self.__get_general_info(info_tables)
        schedule_info_list = self.__get_schedule_info_list(info_tables)
        student_numbers_info = self.__get_student_numbers_info(info_tables)

        for schedule_info in schedule_info_list:
            result.append(general_info | schedule_info | student_numbers_info)
        return result

    def __get_general_info(self, info_tables: Any) -> dict:
        result = {}
        general_info_table = info_tables[0]
        general_info_table_rows = general_info_table.find_all("tr")

        class_code = general_info_table_rows[0].find_all("td")[1].get_text(strip=True)
        start_period = general_info_table_rows[1].find_all("td")[1].get_text(strip=True)
        end_period = general_info_table_rows[2].find_all("td")[1].get_text(strip=True)
        class_type = general_info_table_rows[3].find_all("td")[1].get_text(strip=True)
        try:
            obs = general_info_table_rows[4].find_all("td")[1].get_text(strip=True)
        except IndexError:
            obs = ""

        result["class_code"] = class_code
        result["start_period"] = start_period
        result["end_period"] = end_period
        result["start_period"] = datetime.strptime(start_period, "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )
        result["end_period"] = datetime.strptime(end_period, "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )
        result["type"] = class_type
        result["obs"] = obs

        return result

    def __get_schedule_info_list(self, info_tables: Any) -> list:
        result = []
        schedule_info_table = info_tables[1]
        schedule_info_rows = schedule_info_table.find_all("tr")
        schedule_info_rows_dropped = schedule_info_rows[1:]
        schedule_info_enumerate = enumerate(schedule_info_rows_dropped)

        for _, row in schedule_info_enumerate:
            partial_result = {}
            data = row.find_all("td")

            week_day = data[0].get_text(strip=True)
            start_time = data[1].get_text(strip=True)
            end_time = data[2].get_text(strip=True)
            professor = data[3].get_text(strip=True)

            # More than one professor: only the first row has info, the others only have
            # the additional professor
            if (
                week_day == ""
                and start_time == ""
                and end_time == ""
                and professor != ""
            ):
                result[len(result) - 1]["professors"].append(professor)
                continue

            # More than one hour in same day: only week day is empty
            if (
                week_day == ""
                and start_time != ""
                and end_time != ""
                and professor != ""
            ):
                week_day = result[len(result) - 1]["week_day"]

            partial_result["week_day"] = week_day
            partial_result["professors"] = [professor]
            partial_result["start_time"] = start_time
            partial_result["end_time"] = end_time
            result.append(partial_result)

        return result

    def __get_student_numbers_info(self, info_tables: Any) -> dict:
        result = {
            "vacancies": 0,
            "subscribers": 0,
            "pendings": 0,
            "enrolled": 0,
        }
        student_numbers_table = info_tables[2]
        student_numbers_rows = student_numbers_table.find_all("tr")

        # drop the first row, which is the header:
        student_numbers_rows_dropped = student_numbers_rows[1:]

        filter = {"class": "txt_arial_8pt_black"}
        for row in student_numbers_rows_dropped:
            data = row.find_all("span", attrs=filter)

            # The filter is of black text. If the data is empty, it means that the text on
            # the row is not black, so it should be ignored
            if data == []:
                continue

            if len(data) == 6:
                # drop the first column, which is an empty one:
                data.pop(0)

            vacancies_text = data[1].get_text(strip=True)
            subscribers_text = data[2].get_text(strip=True)
            pendings_text = data[3].get_text(strip=True)
            enrolled_text = data[4].get_text(strip=True)

            if vacancies_text != "" and vacancies_text.isdigit():
                result["vacancies"] += int(vacancies_text)
            if subscribers_text != "" and subscribers_text.isdigit():
                result["subscribers"] += int(subscribers_text)
            if pendings_text != "" and pendings_text.isdigit():
                result["pendings"] += int(pendings_text)
            if enrolled_text != "" and enrolled_text.isdigit():
                result["enrolled"] += int(enrolled_text)

        return result

    def __add_subject_info_to_events(self) -> Any:
        self.__get_subject_name()
        for event in self.events:
            event["subject_name"] = self.subject_name
            event["subject_code"] = self.subject_code

    def __get_subject_name(self) -> Any:
        subject = self.soup.find_all("b", text=re.compile("Disciplina:(.*)"))[0]
        self.subject_name = subject.get_text().replace(
            f"Disciplina: {self.subject_code} - ", ""
        )


if __name__ == "__main__":
    result = JupiterCrawler.crawl_subject_static("PEA3306")
    print(result)
