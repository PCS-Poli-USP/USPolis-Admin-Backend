from typing import TypedDict
from sqlmodel import Session
from server.models.database.class_db_model import Class
from server.repositories.class_repository import ClassRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.deps.interval_dep import QueryInterval
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay

from datetime import time, date

from server.utils.must_be_int import must_be_int


class OccuppanceReportDict(TypedDict):
    week_day: WeekDay | None
    classroom: str
    capacity: int
    classes: list[str]
    start_time: time
    end_time: time
    students: int
    percentage: float
    class_id: list[int | None]


class OccupanceReportsService:
    @staticmethod
    def get_occupance_reports(
        session: Session, building_id: int, interval: QueryInterval
    ) -> list[OccuppanceReportDict]:
        occupance_reports: list[OccuppanceReportDict] = []

        classrooms = ClassroomRepository.get_all_on_buildings(
            building_ids=[building_id], session=session
        )
        classroom_ids = [
            must_be_int(c.id) for c in classrooms
        ]  # excluir caso do Unknown (if c.id is not None deixa de lado o Unknown)
        classes = ClassRepository.get_all_on_classrooms(
            classroom_ids=classroom_ids, session=session, interval=interval
        )

        # (classroom_id, week_day, start_time, end_time) é a chave - list é uma lista de classes (valor associado a chave)
        schedule_map: dict[
            tuple[int, WeekDay | None, time, time], list[Class]
        ] = {}  # dicionario vazio - tuple (lista imutável)

        for class_ in classes:
            schedules = ScheduleRepository.get_all_on_class(
                class_=class_, session=session
            )  # pegar as agendas de uma sala

            for schedule in schedules:
                if (
                    not schedule.classroom_id
                    or not schedule.start_date
                    or not schedule.end_date
                ):  # são NOne
                    continue  # pula para o próximo schedule

                if schedule.recurrence in [Recurrence.WEEKLY, Recurrence.DAILY]:
                    key = (
                        schedule.classroom_id,
                        schedule.week_day,
                        schedule.start_time,
                        schedule.end_time,
                    )
                    schedule_map.setdefault(key, []).append(
                        class_
                    )  # se ainda não existe, cria; se existe, adiciona class_ a essa chave

        for (classroom_id, week_day, start, end), class_list in schedule_map.items():
            classroom = ClassroomRepository.get_by_id(id=classroom_id, session=session)

            total_students = sum(c.vacancies for c in class_list)
            if classroom.capacity > 0:
                percentage_occupance = (total_students / classroom.capacity) * 100
                occupance_reports.append(
                    {
                        "week_day": week_day,
                        "classroom": classroom.name,
                        "capacity": classroom.capacity,
                        "classes": [
                            f"{c.subject.code} - {c.subject.name} ({c.code})"
                            for c in class_list
                        ],
                        "start_time": start,
                        "end_time": end,
                        "students": total_students,
                        "percentage": percentage_occupance,
                        "class_id": [c.id for c in class_list],
                    }
                )

        return occupance_reports
