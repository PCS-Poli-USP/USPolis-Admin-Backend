from datetime import date

import pytest
from sqlmodel import Session

from server.models.database.calendar_db_model import Calendar
from server.models.database.user_db_model import User
from server.repositories.calendar_repository import (
    CalendarAlreadyExists,
    CalendarNotFound,
    CalendarOperationNotAllowed,
    CalendarRepository,
)
from server.utils.must_be_int import must_be_int
from tests.factories.model.calendar_model_factory import CalendarModelFactory
from tests.factories.model.holiday_category_model_factory import (
    HolidayCategoryModelFactory,
)
from tests.factories.request.calendar_request_factory import CalendarRequestFactory


class TestGetAll:
    def test_returns_every_calendar(self, admin_user: User, session: Session) -> None:
        calendar = CalendarModelFactory(admin_user, session).create_and_refresh()

        calendars = CalendarRepository.get_all(session=session)

        assert calendar.id in [c.id for c in calendars]


class TestGetAllOnYear:
    def test_returns_only_calendars_of_the_given_year(
        self, admin_user: User, session: Session
    ) -> None:
        this_year = CalendarModelFactory(admin_user, session).create_and_refresh(
            year=2030
        )
        CalendarModelFactory(admin_user, session).create_and_refresh(year=2031)

        calendars = CalendarRepository.get_all_on_year(session=session, year=2030)

        assert [c.id for c in calendars] == [this_year.id]


class TestGetAllFromNow:
    def test_excludes_calendars_from_past_years(
        self, admin_user: User, session: Session
    ) -> None:
        current_year = date.today().year
        current = CalendarModelFactory(admin_user, session).create_and_refresh(
            year=current_year
        )
        past = CalendarModelFactory(admin_user, session).create_and_refresh(
            year=current_year - 5
        )

        calendars = CalendarRepository.get_all_from_now(session=session)

        ids = [c.id for c in calendars]
        assert current.id in ids
        assert past.id not in ids


class TestGetById:
    def test_returns_the_matching_calendar(
        self, admin_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(admin_user, session).create_and_refresh()

        found = CalendarRepository.get_by_id(id=must_be_int(calendar.id), session=session)

        assert found.id == calendar.id

    def test_raises_for_an_unknown_id(self, session: Session) -> None:
        with pytest.raises(CalendarNotFound):
            CalendarRepository.get_by_id(id=-1, session=session)


class TestGetByIds:
    def test_returns_only_the_matching_calendars(
        self, admin_user: User, session: Session
    ) -> None:
        wanted = CalendarModelFactory(admin_user, session).create_and_refresh()
        CalendarModelFactory(admin_user, session).create_and_refresh()

        found = CalendarRepository.get_by_ids(
            ids=[must_be_int(wanted.id)], session=session
        )

        assert [c.id for c in found] == [wanted.id]


class TestGetByName:
    def test_returns_the_matching_calendar(
        self, admin_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(admin_user, session).create_and_refresh()

        found = CalendarRepository.get_by_name(name=calendar.name, session=session)

        assert found.id == calendar.id

    def test_raises_for_an_unknown_name(self, session: Session) -> None:
        with pytest.raises(CalendarNotFound):
            CalendarRepository.get_by_name(name="does-not-exist", session=session)


class TestCreate:
    def test_creates_a_calendar(self, admin_user: User, session: Session) -> None:
        input = CalendarRequestFactory().create_input()

        calendar = CalendarRepository.create(
            creator=admin_user, input=input, session=session
        )

        assert calendar.name == input.name
        assert calendar.year == input.year
        assert calendar.categories == []

    def test_creates_a_calendar_with_categories(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        input = CalendarRequestFactory(
            categories_ids=[must_be_int(category.id)]
        ).create_input()

        calendar = CalendarRepository.create(
            creator=admin_user, input=input, session=session
        )

        assert [c.id for c in calendar.categories] == [category.id]

    def test_raises_on_duplicate_name_and_year(
        self, admin_user: User, session: Session
    ) -> None:
        existing = CalendarModelFactory(admin_user, session).create_and_refresh()
        input = CalendarRequestFactory().create_input(
            name=existing.name, year=existing.year
        )

        with pytest.raises(CalendarAlreadyExists):
            CalendarRepository.create(creator=admin_user, input=input, session=session)


class TestUpdate:
    def test_admin_can_update_any_calendar(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(common_user, session).create_and_refresh()
        input = CalendarRequestFactory().update_input(name="Novo Calendário")

        updated = CalendarRepository.update(
            id=must_be_int(calendar.id), input=input, user=admin_user, session=session
        )

        assert updated.name == "Novo Calendário"

    def test_owner_can_update_their_own_calendar(
        self, common_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(common_user, session).create_and_refresh()
        input = CalendarRequestFactory().update_input(name="Novo Calendário")

        updated = CalendarRepository.update(
            id=must_be_int(calendar.id), input=input, user=common_user, session=session
        )

        assert updated.name == "Novo Calendário"

    def test_updates_the_linked_categories(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        calendar = CalendarModelFactory(admin_user, session).create_and_refresh()
        input = CalendarRequestFactory(
            categories_ids=[must_be_int(category.id)]
        ).update_input()

        updated = CalendarRepository.update(
            id=must_be_int(calendar.id), input=input, user=admin_user, session=session
        )

        assert [c.id for c in updated.categories] == [category.id]

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(admin_user, session).create_and_refresh()
        input = CalendarRequestFactory().update_input()

        with pytest.raises(CalendarOperationNotAllowed):
            CalendarRepository.update(
                id=must_be_int(calendar.id),
                input=input,
                user=common_user,
                session=session,
            )


class TestDelete:
    def test_admin_can_delete_any_calendar(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(common_user, session).create_and_refresh()
        calendar_id = must_be_int(calendar.id)

        CalendarRepository.delete(id=calendar_id, user=admin_user, session=session)

        assert session.get(Calendar, calendar_id) is None

    def test_owner_can_delete_their_own_calendar(
        self, common_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(common_user, session).create_and_refresh()
        calendar_id = must_be_int(calendar.id)

        CalendarRepository.delete(id=calendar_id, user=common_user, session=session)

        assert session.get(Calendar, calendar_id) is None

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        calendar = CalendarModelFactory(admin_user, session).create_and_refresh()

        with pytest.raises(CalendarOperationNotAllowed):
            CalendarRepository.delete(
                id=must_be_int(calendar.id), user=common_user, session=session
            )
