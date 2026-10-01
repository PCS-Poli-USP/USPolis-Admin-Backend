import pytest
from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.subject_repository_adapter import (
    SubjectAlreadyExists,
    SubjectRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.services.security.buildings_permission_checker import (
    ForbiddenBuildingAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.subjects_permission_checker import (
    ForbiddenSubjectAccess,
)
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int
from tests.factories.request.subject_request_factory import SubjectRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> SubjectRepositoryAdapter:
    return SubjectRepositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        session=session,
        user=user,
        permission_index=build_permission_index(user),
    )


class TestGetAll:
    def test_admin_sees_every_subject(
        self, admin_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)

        subjects = adapter.get_all()

        assert subject.id in [s.id for s in subjects]

    def test_restricted_user_sees_subjects_of_owned_buildings(
        self, restricted_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        subjects = adapter.get_all()

        assert subject.id in [s.id for s in subjects]

    def test_common_user_sees_none(
        self, common_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        assert subject.id not in [s.id for s in adapter.get_all()]


class TestGetById:
    def test_denies_without_permission(
        self, common_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenSubjectAccess):
            adapter.get_by_id(must_be_int(subject.id))

    def test_allows_via_granted_permission(
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
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_id(must_be_int(subject.id))

        assert found.id == subject.id


class TestGetByCode:
    def test_denies_without_permission(
        self, common_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenSubjectAccess):
            adapter.get_by_code(subject.code)

    def test_allows_via_granted_permission(
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
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_code(subject.code)

        assert found.id == subject.id


class TestCreate:
    def test_denies_without_permission(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).create_input()

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.create(input)

    def test_creates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
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
        input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).create_input()

        created = adapter.create(input)

        assert created.code == input.code

    def test_raises_on_duplicate_code(
        self, admin_user: User, building: Building, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)
        input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).create_input(code=subject.code)

        with pytest.raises(SubjectAlreadyExists):
            adapter.create(input)


class TestUpdate:
    def test_denies_without_permission(
        self, common_user: User, building: Building, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).update_input()

        with pytest.raises(ForbiddenSubjectAccess):
            adapter.update(must_be_int(subject.id), input)

    def test_updates_via_granted_permission(
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
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).update_input(name="Nova Disciplina")

        updated = adapter.update(must_be_int(subject.id), input)

        assert updated.name == "Nova Disciplina"


class TestDelete:
    def test_denies_without_permission(
        self, common_user: User, subject: Subject, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenSubjectAccess):
            adapter.delete(must_be_int(subject.id))

    def test_deletes_via_granted_permission(
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
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        subject_id = must_be_int(subject.id)

        adapter.delete(subject_id)
        session.commit()

        assert session.get(Subject, subject_id) is None
