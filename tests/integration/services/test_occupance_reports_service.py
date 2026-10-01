from datetime import time

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.services.occupance_reports_service import OccupanceReportsService
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay
from server.utils.must_be_int import must_be_int
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory


def make_allocated_class(
    *,
    subject: Subject,
    classroom: Classroom,
    session: Session,
    start_time: time = time(8, 0),
    end_time: time = time(10, 0),
    week_day: WeekDay | None = WeekDay.MONDAY,
    recurrence: Recurrence = Recurrence.WEEKLY,
    vacancies: int = 30,
) -> Class:
    class_ = ClassModelFactory(subject=subject, session=session).create_and_refresh(
        schedules=[], vacancies=vacancies
    )
    ScheduleModelFactory(class_=class_, session=session).create_and_refresh(
        classroom_id=classroom.id,
        classroom=classroom,
        start_time=start_time,
        end_time=end_time,
        week_day=week_day,
        recurrence=recurrence,
        allocated=True,
    )
    session.refresh(class_)
    return class_


@pytest.fixture(name="report_interval")
def report_interval_fixture(class_: Class) -> QueryInterval:
    # class_ is only depended on here to force fixture ordering - its own
    # default schedule is unallocated and irrelevant to these tests.
    return QueryInterval(start=class_.start_date, end=class_.end_date)


class TestGetOccupanceReports:
    def test_returns_empty_list_when_building_has_no_classrooms(
        self, building: Building, report_interval: QueryInterval, session: Session
    ) -> None:
        reports = OccupanceReportsService.get_occupance_reports(
            session=session,
            building_id=must_be_int(building.id),
            interval=report_interval,
        )
        assert reports == []

    def test_returns_report_for_a_single_allocated_weekly_class(
        self,
        building: Building,
        subject: Subject,
        classroom: Classroom,
        session: Session,
    ) -> None:
        allocated = make_allocated_class(
            subject=subject,
            classroom=classroom,
            session=session,
            start_time=time(8, 0),
            end_time=time(10, 0),
            week_day=WeekDay.MONDAY,
            vacancies=30,
        )
        classroom.capacity = 50
        session.add(classroom)
        session.commit()
        interval = QueryInterval(start=allocated.start_date, end=allocated.end_date)

        reports = OccupanceReportsService.get_occupance_reports(
            session=session, building_id=must_be_int(building.id), interval=interval
        )

        assert len(reports) == 1
        report = reports[0]
        assert report["classroom"] == classroom.name
        assert report["capacity"] == 50
        assert report["week_day"] == WeekDay.MONDAY
        assert report["start_time"] == time(8, 0)
        assert report["end_time"] == time(10, 0)
        assert report["students"] == 30
        assert report["percentage"] == pytest.approx(60.0)
        assert report["class_id"] == [allocated.id]
        assert report["classes"] == [
            f"{allocated.subject.code} - {allocated.subject.name} ({allocated.code})"
        ]

    def test_groups_multiple_classes_sharing_the_same_slot(
        self,
        building: Building,
        subject: Subject,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.capacity = 100
        session.add(classroom)
        session.commit()

        first = make_allocated_class(
            subject=subject,
            classroom=classroom,
            session=session,
            start_time=time(8, 0),
            end_time=time(10, 0),
            week_day=WeekDay.TUESDAY,
            vacancies=20,
        )
        second = make_allocated_class(
            subject=subject,
            classroom=classroom,
            session=session,
            start_time=time(8, 0),
            end_time=time(10, 0),
            week_day=WeekDay.TUESDAY,
            vacancies=15,
        )
        interval = QueryInterval(start=first.start_date, end=first.end_date)

        reports = OccupanceReportsService.get_occupance_reports(
            session=session, building_id=must_be_int(building.id), interval=interval
        )

        assert len(reports) == 1
        report = reports[0]
        assert report["students"] == 35
        assert report["percentage"] == pytest.approx(35.0)
        assert set(report["class_id"]) == {first.id, second.id}
        assert len(report["classes"]) == 2

    def test_excludes_schedules_without_a_classroom(
        self,
        building: Building,
        class_: Class,
        report_interval: QueryInterval,
        session: Session,
    ) -> None:
        # class_'s default schedule is never allocated to any classroom.
        assert class_.schedules[0].classroom_id is None

        reports = OccupanceReportsService.get_occupance_reports(
            session=session,
            building_id=must_be_int(building.id),
            interval=report_interval,
        )
        assert reports == []

    def test_excludes_non_weekly_or_daily_recurrences(
        self,
        building: Building,
        subject: Subject,
        classroom: Classroom,
        session: Session,
    ) -> None:
        allocated = make_allocated_class(
            subject=subject,
            classroom=classroom,
            session=session,
            recurrence=Recurrence.MONTHLY,
        )
        interval = QueryInterval(start=allocated.start_date, end=allocated.end_date)

        reports = OccupanceReportsService.get_occupance_reports(
            session=session, building_id=must_be_int(building.id), interval=interval
        )
        assert reports == []

    def test_includes_daily_recurrence(
        self,
        building: Building,
        subject: Subject,
        classroom: Classroom,
        session: Session,
    ) -> None:
        allocated = make_allocated_class(
            subject=subject,
            classroom=classroom,
            session=session,
            recurrence=Recurrence.DAILY,
            week_day=None,
        )
        interval = QueryInterval(start=allocated.start_date, end=allocated.end_date)

        reports = OccupanceReportsService.get_occupance_reports(
            session=session, building_id=must_be_int(building.id), interval=interval
        )
        assert len(reports) == 1
        assert reports[0]["week_day"] is None

    def test_excludes_classrooms_with_zero_capacity(
        self,
        building: Building,
        subject: Subject,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.capacity = 0
        session.add(classroom)
        session.commit()
        allocated = make_allocated_class(
            subject=subject, classroom=classroom, session=session
        )
        interval = QueryInterval(start=allocated.start_date, end=allocated.end_date)

        reports = OccupanceReportsService.get_occupance_reports(
            session=session, building_id=must_be_int(building.id), interval=interval
        )
        assert reports == []

    def test_percentage_can_exceed_100_when_overbooked(
        self,
        building: Building,
        subject: Subject,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.capacity = 10
        session.add(classroom)
        session.commit()
        allocated = make_allocated_class(
            subject=subject, classroom=classroom, session=session, vacancies=25
        )
        interval = QueryInterval(start=allocated.start_date, end=allocated.end_date)

        reports = OccupanceReportsService.get_occupance_reports(
            session=session, building_id=must_be_int(building.id), interval=interval
        )
        assert len(reports) == 1
        assert reports[0]["percentage"] == pytest.approx(250.0)
