from datetime import datetime, time

import pytest
from sqlmodel import Session

from server.models.database.holiday_db_model import Holiday
from server.models.database.user_db_model import User
from server.repositories.holiday_repository import (
    HolidayInCategoryAlreadyExists,
    HolidayNotFound,
    HolidayOperationNotAllowed,
    HolidayRepository,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from tests.factories.model.holiday_category_model_factory import (
    HolidayCategoryModelFactory,
)
from tests.factories.model.holiday_model_factory import HolidayModelFactory
from tests.factories.request.holiday_request_factory import HolidayRequestFactory


class TestGetAll:
    def test_returns_every_holiday(self, admin_user: User, session: Session) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            admin_user, category, session
        ).create_and_refresh()

        holidays = HolidayRepository.get_all(session=session)

        assert holiday.id in [h.id for h in holidays]


class TestGetById:
    def test_returns_the_matching_holiday(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            admin_user, category, session
        ).create_and_refresh()

        found = HolidayRepository.get_by_id(id=must_be_int(holiday.id), session=session)

        assert found.id == holiday.id

    def test_raises_for_an_unknown_id(self, session: Session) -> None:
        with pytest.raises(HolidayNotFound):
            HolidayRepository.get_by_id(id=-1, session=session)


class TestCheckDateIsValid:
    def test_returns_true_when_no_holiday_exists_on_the_date(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()

        is_valid = HolidayRepository.check_date_is_valid(
            category_id=must_be_int(category.id),
            date=BrazilDatetime.now_utc(),
            session=session,
        )

        assert is_valid is True

    def test_returns_false_when_a_holiday_already_exists_on_the_date(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        date = BrazilDatetime.now_utc()
        HolidayModelFactory(admin_user, category, session).create_and_refresh(date=date)

        is_valid = HolidayRepository.check_date_is_valid(
            category_id=must_be_int(category.id), date=date, session=session
        )

        assert is_valid is False


class TestCreate:
    def test_creates_a_holiday(self, admin_user: User, session: Session) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).create_input()

        holiday = HolidayRepository.create(
            creator=admin_user, input=input, session=session
        )

        assert holiday.name == input.name
        assert holiday.category_id == category.id

    def test_owner_of_the_category_can_create_a_holiday_in_it(
        self, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).create_input()

        holiday = HolidayRepository.create(
            creator=common_user, input=input, session=session
        )

        assert holiday.category_id == category.id

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).create_input()

        with pytest.raises(HolidayOperationNotAllowed):
            HolidayRepository.create(creator=common_user, input=input, session=session)

    def test_raises_on_duplicate_date_in_the_same_category(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        existing = HolidayModelFactory(
            admin_user, category, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).create_input(
            date=datetime.combine(existing.date, time())
        )

        with pytest.raises(HolidayInCategoryAlreadyExists):
            HolidayRepository.create(creator=admin_user, input=input, session=session)


class TestCreateMany:
    def test_creates_a_holiday_for_every_date(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).create_many_input()

        holidays = HolidayRepository.create_many(
            creator=admin_user, input=input, session=session
        )

        assert len(holidays) == len(input.dates)
        assert {h.date for h in holidays} == {d.date() for d in input.dates}


class TestUpdate:
    def test_admin_can_update_any_holiday(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            common_user, category, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).update_input(name="Feriado")

        updated = HolidayRepository.update(
            id=must_be_int(holiday.id), input=input, user=admin_user, session=session
        )

        assert updated.name == "Feriado"

    def test_owner_can_update_their_own_holiday(
        self, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            common_user, category, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).update_input(name="Feriado")

        updated = HolidayRepository.update(
            id=must_be_int(holiday.id), input=input, user=common_user, session=session
        )

        assert updated.name == "Feriado"

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            admin_user, category, session
        ).create_and_refresh()
        input = HolidayRequestFactory(category=category).update_input()

        with pytest.raises(HolidayOperationNotAllowed):
            HolidayRepository.update(
                id=must_be_int(holiday.id),
                input=input,
                user=common_user,
                session=session,
            )


class TestDelete:
    def test_admin_can_delete_any_holiday(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            common_user, category, session
        ).create_and_refresh()
        holiday_id = must_be_int(holiday.id)

        HolidayRepository.delete(id=holiday_id, user=admin_user, session=session)

        assert session.get(Holiday, holiday_id) is None

    def test_owner_can_delete_their_own_holiday(
        self, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            common_user, category, session
        ).create_and_refresh()
        holiday_id = must_be_int(holiday.id)

        HolidayRepository.delete(id=holiday_id, user=common_user, session=session)

        assert session.get(Holiday, holiday_id) is None

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        holiday = HolidayModelFactory(
            admin_user, category, session
        ).create_and_refresh()

        with pytest.raises(HolidayOperationNotAllowed):
            HolidayRepository.delete(
                id=must_be_int(holiday.id), user=common_user, session=session
            )
