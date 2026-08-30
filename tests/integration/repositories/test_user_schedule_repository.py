from datetime import date, timedelta

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.database.user_schedule_entry_db_model import UserScheduleEntry
from server.repositories.user_schedule_repository import UserScheduleRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.schedule_model_factory import ScheduleModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.model.user_schedule_entry_model_factory import (
    UserScheduleEntryModelFactory,
)
from tests.factories.model.user_schedule_model_factory import UserScheduleModelFactory

TODAY = date.today()
ACTIVE_END = TODAY + timedelta(days=30)
EXPIRED_END = TODAY - timedelta(days=1)


def _active_schedule(session: Session, **overrides: object) -> Schedule:
    defaults: dict[str, object] = {
        "start_date": TODAY,
        "end_date": ACTIVE_END,
    }
    defaults.update(overrides)
    return ScheduleModelFactory(session=session).create_and_refresh(**defaults)  # type: ignore[arg-type]


def _expired_schedule(session: Session) -> Schedule:
    return ScheduleModelFactory(session=session).create_and_refresh(
        start_date=TODAY - timedelta(days=60), end_date=EXPIRED_END
    )


class TestGetById:
    def test_returns_the_matching_user_schedule(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh()

        found = UserScheduleRepository.get_by_id(
            id=must_be_int(user_schedule.id), session=session
        )

        assert found is not None
        assert found.id == user_schedule.id

    def test_returns_none_for_an_unknown_id(self, session: Session) -> None:
        assert UserScheduleRepository.get_by_id(id=999999, session=session) is None


class TestGetActiveCurrentSchedule:
    def test_returns_none_when_the_user_has_no_current_schedule(
        self, admin_user: User, session: Session
    ) -> None:
        result, expired = UserScheduleRepository.get_active_current_schedule(
            user=admin_user, session=session
        )

        assert result is None
        assert expired is False

    def test_returns_the_schedule_when_it_is_still_active(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh(start_date=TODAY, end_date=ACTIVE_END)
        admin_user.current_schedule = user_schedule
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        result, expired = UserScheduleRepository.get_active_current_schedule(
            user=admin_user, session=session
        )

        assert result is not None
        assert result.id == user_schedule.id
        assert expired is False

    def test_clears_and_reports_an_expired_current_schedule(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh(
            start_date=TODAY - timedelta(days=60), end_date=EXPIRED_END
        )
        admin_user.current_schedule = user_schedule
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        result, expired = UserScheduleRepository.get_active_current_schedule(
            user=admin_user, session=session
        )
        session.commit()
        session.refresh(admin_user)

        assert result is None
        assert expired is True
        assert admin_user.current_schedule_id is None


class TestInvalidateExpiredCurrentSchedules:
    def test_invalidates_only_users_with_an_expired_current_schedule(
        self, admin_user: User, session: Session
    ) -> None:
        other_user = UserModelFactory(session=session).create_and_refresh()

        expired_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh(
            start_date=TODAY - timedelta(days=60), end_date=EXPIRED_END
        )
        active_schedule = UserScheduleModelFactory(
            user=other_user, session=session
        ).create_and_refresh(start_date=TODAY, end_date=ACTIVE_END)

        admin_user.current_schedule = expired_schedule
        other_user.current_schedule = active_schedule
        session.add(admin_user)
        session.add(other_user)
        session.commit()

        invalidated_ids = UserScheduleRepository.invalidate_expired_current_schedules(
            session=session
        )
        session.commit()
        session.refresh(admin_user)
        session.refresh(other_user)

        assert invalidated_ids == [expired_schedule.id]
        assert admin_user.current_schedule_id is None
        assert other_user.current_schedule_id == active_schedule.id


class TestUpdateFromSchedules:
    def test_raises_when_a_schedule_is_not_active(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh()
        inactive = _expired_schedule(session)

        with pytest.raises(HTTPException):
            UserScheduleRepository.update_from_schedules(
                user_schedule=user_schedule, schedules=[inactive], session=session
            )

    def test_sets_start_and_end_date_from_the_given_schedules(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh()
        early = _active_schedule(
            session, start_date=TODAY, end_date=TODAY + timedelta(days=10)
        )
        late = _active_schedule(
            session, start_date=TODAY + timedelta(days=5), end_date=ACTIVE_END
        )

        updated = UserScheduleRepository.update_from_schedules(
            user_schedule=user_schedule, schedules=[early, late], session=session
        )
        session.commit()
        session.refresh(updated)

        assert updated.start_date == TODAY
        assert updated.end_date == ACTIVE_END
        assert {e.schedule_id for e in updated.entries} == {early.id, late.id}

    def test_with_no_schedules_defaults_to_today_and_clears_entries(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh()
        schedule = _active_schedule(session)
        UserScheduleRepository.update_from_schedules(
            user_schedule=user_schedule, schedules=[schedule], session=session
        )
        session.commit()

        updated = UserScheduleRepository.update_from_schedules(
            user_schedule=user_schedule, schedules=[], session=session
        )
        session.commit()
        session.refresh(updated)

        assert updated.start_date == TODAY
        assert updated.end_date == TODAY
        assert updated.entries == []

    def test_deduplicates_repeated_schedules(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh()
        schedule = _active_schedule(session)

        updated = UserScheduleRepository.update_from_schedules(
            user_schedule=user_schedule,
            schedules=[schedule, schedule],
            session=session,
        )
        session.commit()
        session.refresh(updated)

        assert len(updated.entries) == 1

    def test_preserves_the_existing_entry_for_a_schedule_that_stays(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleModelFactory(
            user=admin_user, session=session
        ).create_and_refresh()
        kept_schedule = _active_schedule(session)
        removed_schedule = _active_schedule(session)

        kept_entry = UserScheduleEntryModelFactory(
            user_schedule=user_schedule, schedule=kept_schedule, session=session
        ).create_and_refresh(absence_count=3)
        UserScheduleEntryModelFactory(
            user_schedule=user_schedule, schedule=removed_schedule, session=session
        ).create_and_refresh()
        session.commit()
        session.refresh(user_schedule)

        updated = UserScheduleRepository.update_from_schedules(
            user_schedule=user_schedule, schedules=[kept_schedule], session=session
        )
        session.commit()
        session.refresh(updated)

        assert [e.schedule_id for e in updated.entries] == [kept_schedule.id]
        assert updated.entries[0].absence_count == 3

        remaining_links = session.exec(
            select(UserScheduleEntry).where(
                UserScheduleEntry.user_schedule_id == user_schedule.id
            )
        ).all()
        assert {link.schedule_id for link in remaining_links} == {kept_schedule.id}
        assert kept_entry.schedule_id == kept_schedule.id


class TestCreateFromSchedules:
    def test_raises_when_a_schedule_is_not_active(
        self, admin_user: User, session: Session
    ) -> None:
        inactive = _expired_schedule(session)

        with pytest.raises(HTTPException):
            UserScheduleRepository.create_from_schedules(
                user=admin_user, schedules=[inactive], session=session
            )

    def test_creates_a_user_schedule_with_entries_for_every_schedule(
        self, admin_user: User, session: Session
    ) -> None:
        schedule1 = _active_schedule(
            session, start_date=TODAY, end_date=TODAY + timedelta(days=10)
        )
        schedule2 = _active_schedule(
            session, start_date=TODAY + timedelta(days=5), end_date=ACTIVE_END
        )

        user_schedule = UserScheduleRepository.create_from_schedules(
            user=admin_user, schedules=[schedule1, schedule2], session=session
        )
        session.commit()
        session.refresh(user_schedule)

        assert user_schedule.user_id == admin_user.id
        assert user_schedule.start_date == TODAY
        assert user_schedule.end_date == ACTIVE_END
        assert {e.schedule_id for e in user_schedule.entries} == {
            schedule1.id,
            schedule2.id,
        }

    def test_with_no_schedules_defaults_to_today_with_no_entries(
        self, admin_user: User, session: Session
    ) -> None:
        user_schedule = UserScheduleRepository.create_from_schedules(
            user=admin_user, schedules=[], session=session
        )
        session.commit()
        session.refresh(user_schedule)

        assert user_schedule.start_date == TODAY
        assert user_schedule.end_date == TODAY
        assert user_schedule.entries == []


class TestDelete:
    def test_delete_removes_the_user_schedule_and_its_entries(
        self, admin_user: User, session: Session
    ) -> None:
        schedule = _active_schedule(session)
        user_schedule = UserScheduleRepository.create_from_schedules(
            user=admin_user, schedules=[schedule], session=session
        )
        session.commit()
        session.refresh(user_schedule)
        user_schedule_id = must_be_int(user_schedule.id)

        UserScheduleRepository.delete(user_schedule=user_schedule, session=session)
        session.commit()

        assert UserScheduleRepository.get_by_id(
            id=user_schedule_id, session=session
        ) is None
        remaining_entries = session.exec(
            select(UserScheduleEntry).where(
                UserScheduleEntry.user_schedule_id == user_schedule_id
            )
        ).all()
        assert list(remaining_entries) == []
