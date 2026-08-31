import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.class_repository_adapter import (
    ClassRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.services.security.class_permission_checker import ForbiddenClassAccess
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.subjects_permission_checker import (
    ForbiddenSubjectAccess,
)
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int
from tests.factories.request.class_request_factory import ClassRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> ClassRepositoryAdapter:
    return ClassRepositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        session=session,
        user=user,
        interval=QueryInterval(),
        permission_index=build_permission_index(user),
    )


class TestGetAll:
    def test_admin_sees_every_class(
        self, admin_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)

        classes = adapter.get_all()

        assert class_.id in [c.id for c in classes]

    def test_restricted_user_sees_classes_of_owned_buildings(
        self, restricted_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        classes = adapter.get_all()

        assert class_.id in [c.id for c in classes]

    def test_common_user_sees_none(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        assert class_.id not in [c.id for c in adapter.get_all()]


class TestGetAllOnMyClassrooms:
    def test_returns_classes_scheduled_on_owned_classrooms(
        self,
        restricted_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        classes = adapter.get_all_on_my_classrooms()

        assert class_.id in [c.id for c in classes]


class TestGetAllUnallocated:
    def test_returns_unallocated_classes_of_owned_buildings(
        self, restricted_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        classes = adapter.get_all_unallocated()

        assert class_.id in [c.id for c in classes]


class TestGetAllOnMyBuildings:
    def test_returns_classes_of_owned_buildings(
        self, restricted_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        classes = adapter.get_all_on_my_buildings()

        assert class_.id in [c.id for c in classes]


class TestGetById:
    def test_denies_without_permission(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassAccess):
            adapter.get_by_id(must_be_int(class_.id))

    def test_allows_via_granted_building_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_id(must_be_int(class_.id))

        assert found.id == class_.id


class TestCreate:
    def test_denies_without_permission(
        self, common_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = ClassRequestFactory(subject=subject).create_input()

        with pytest.raises(ForbiddenSubjectAccess):
            adapter.create(input)

    def test_creates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        subject: Subject,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.CREATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = ClassRequestFactory(subject=subject).create_input()

        created = adapter.create(input)

        assert created.code == input.code
        assert len(created.schedules) == 1


class TestUpdate:
    def test_denies_without_permission(
        self, common_user: User, subject: Subject, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = ClassRequestFactory(subject=subject).update_input()

        with pytest.raises(ForbiddenClassAccess):
            adapter.update(must_be_int(class_.id), input)


class TestDelete:
    def test_denies_without_class_permission(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassAccess):
            adapter.delete(must_be_int(class_.id))

    def test_deletes_via_granted_permissions(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        class_id = must_be_int(class_.id)

        adapter.delete(class_id)
        session.commit()

        assert session.get(Class, class_id) is None


class TestDeleteMany:
    def test_denies_when_any_class_lacks_permission(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassAccess):
            adapter.delete_many([must_be_int(class_.id)])

    def test_deletes_via_granted_permissions(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        class_id = must_be_int(class_.id)

        adapter.delete_many([class_id])
        session.commit()

        assert session.get(Class, class_id) is None
