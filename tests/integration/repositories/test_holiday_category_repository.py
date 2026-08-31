import pytest
from sqlmodel import Session

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.user_db_model import User
from server.repositories.holiday_category_repository import (
    HolidayCategoryAlreadyExists,
    HolidayCategoryNotFound,
    HolidayCategoryOperationNotAllowed,
    HolidayCategoryRepository,
)
from server.utils.must_be_int import must_be_int
from tests.factories.model.holiday_category_model_factory import (
    HolidayCategoryModelFactory,
)
from tests.factories.request.holiday_category_request_factory import (
    HolidayCategoryRequestFactory,
)


class TestGetAll:
    def test_returns_every_category_ordered_by_year_desc_then_name(
        self, admin_user: User, session: Session
    ) -> None:
        older_b = HolidayCategoryModelFactory(admin_user, session).create_and_refresh(
            name="B", year=2020
        )
        newer_a = HolidayCategoryModelFactory(admin_user, session).create_and_refresh(
            name="A", year=2024
        )
        newer_b = HolidayCategoryModelFactory(admin_user, session).create_and_refresh(
            name="B", year=2024
        )

        categories = HolidayCategoryRepository.get_all(session=session)

        ids_in_order = [c.id for c in categories]
        assert ids_in_order.index(newer_a.id) < ids_in_order.index(newer_b.id)
        assert ids_in_order.index(newer_b.id) < ids_in_order.index(older_b.id)


class TestGetById:
    def test_returns_the_matching_category(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()

        found = HolidayCategoryRepository.get_by_id(
            id=must_be_int(category.id), session=session
        )

        assert found.id == category.id

    def test_raises_for_an_unknown_id(self, session: Session) -> None:
        with pytest.raises(HolidayCategoryNotFound):
            HolidayCategoryRepository.get_by_id(id=-1, session=session)


class TestGetByIds:
    def test_returns_only_the_matching_categories(
        self, admin_user: User, session: Session
    ) -> None:
        wanted = HolidayCategoryModelFactory(admin_user, session).create_and_refresh()
        HolidayCategoryModelFactory(admin_user, session).create_and_refresh()

        found = HolidayCategoryRepository.get_by_ids(
            ids=[must_be_int(wanted.id)], session=session
        )

        assert [c.id for c in found] == [wanted.id]


class TestGetByName:
    def test_returns_the_matching_category(
        self, admin_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()

        found = HolidayCategoryRepository.get_by_name(
            name=category.name, session=session
        )

        assert found.id == category.id

    def test_raises_for_an_unknown_name(self, session: Session) -> None:
        with pytest.raises(HolidayCategoryNotFound):
            HolidayCategoryRepository.get_by_name(
                name="does-not-exist", session=session
            )


class TestCreate:
    def test_creates_a_category(self, admin_user: User, session: Session) -> None:
        input = HolidayCategoryRequestFactory().create_input()

        category = HolidayCategoryRepository.create(
            creator=admin_user, input=input, session=session
        )

        assert category.name == input.name
        assert category.year == input.year
        assert category.created_by_id == admin_user.id

    def test_raises_on_duplicate_name_and_year(
        self, admin_user: User, session: Session
    ) -> None:
        existing = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        input = HolidayCategoryRequestFactory().create_input(
            name=existing.name, year=existing.year
        )

        with pytest.raises(HolidayCategoryAlreadyExists):
            HolidayCategoryRepository.create(
                creator=admin_user, input=input, session=session
            )


class TestUpdate:
    def test_admin_can_update_any_category(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        input = HolidayCategoryRequestFactory().update_input(name="Novo Nome")

        updated = HolidayCategoryRepository.update(
            id=must_be_int(category.id), input=input, user=admin_user, session=session
        )

        assert updated.name == "Novo Nome"

    def test_owner_can_update_their_own_category(
        self, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        input = HolidayCategoryRequestFactory().update_input(name="Novo Nome")

        updated = HolidayCategoryRepository.update(
            id=must_be_int(category.id), input=input, user=common_user, session=session
        )

        assert updated.name == "Novo Nome"

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()
        input = HolidayCategoryRequestFactory().update_input()

        with pytest.raises(HolidayCategoryOperationNotAllowed):
            HolidayCategoryRepository.update(
                id=must_be_int(category.id),
                input=input,
                user=common_user,
                session=session,
            )


class TestDelete:
    def test_admin_can_delete_any_category(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        category_id = must_be_int(category.id)

        HolidayCategoryRepository.delete(
            id=category_id, user=admin_user, session=session
        )

        assert session.get(HolidayCategory, category_id) is None

    def test_owner_can_delete_their_own_category(
        self, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            common_user, session
        ).create_and_refresh()
        category_id = must_be_int(category.id)

        HolidayCategoryRepository.delete(
            id=category_id, user=common_user, session=session
        )

        assert session.get(HolidayCategory, category_id) is None

    def test_denies_a_non_owner_non_admin(
        self, admin_user: User, common_user: User, session: Session
    ) -> None:
        category = HolidayCategoryModelFactory(
            admin_user, session
        ).create_and_refresh()

        with pytest.raises(HolidayCategoryOperationNotAllowed):
            HolidayCategoryRepository.delete(
                id=must_be_int(category.id), user=common_user, session=session
            )
