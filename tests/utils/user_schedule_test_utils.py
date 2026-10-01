"""Shared, DB-free helpers for building UserSchedule/UserScheduleEntry/
UserAbsence object graphs in pure unit tests (no session, nothing
persisted).

These delegate to the real tests/factories/model/*ModelFactory classes via
their session-free `.build()` method, same as academic_test_utils.py and
time_test_utils.py - see TESTS.md's "Test data protocol" section before
adding a new make_* helper here. UserAbsence has no factory/dict scaffolding
of its own yet and is constructed directly instead."""

from datetime import date, datetime

from sqlmodel import Session

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_absence import UserAbsence
from server.models.database.user_db_model import User
from server.models.database.user_schedule_db_model import UserSchedule
from server.models.database.user_schedule_entry_db_model import UserScheduleEntry
from tests.factories.model.user_schedule_entry_model_factory import (
    UserScheduleEntryModelFactory,
)
from tests.factories.model.user_schedule_model_factory import UserScheduleModelFactory

_next_id = iter(range(1, 1_000_000))


def make_user_schedule(*, user: User) -> UserSchedule:
    user_schedule = UserScheduleModelFactory(user, Session()).build()
    user_schedule.id = next(_next_id)
    user_schedule.user = user
    return user_schedule


def make_user_schedule_entry(
    *, user_schedule: UserSchedule, schedule: Schedule
) -> UserScheduleEntry:
    entry = UserScheduleEntryModelFactory(user_schedule, schedule, Session()).build()
    entry.user_schedule = user_schedule
    entry.schedule = schedule
    entry.absences = []
    return entry


def make_user_absence(
    *,
    user_schedule_id: int,
    schedule_id: int,
    absence_date: date = date(2025, 3, 10),
    note: str = "Ausência",
) -> UserAbsence:
    return UserAbsence(
        id=next(_next_id),
        user_schedule_id=user_schedule_id,
        schedule_id=schedule_id,
        absence_date=absence_date,
        note=note,
        updated_at=datetime(2025, 3, 10),
        created_at=datetime(2025, 3, 10),
    )
