import pytest
from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.solicitation_repository_adapter import (
    SolicitationRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.solicitation_request_models import (
    MeetingSolicitation,
    SolicitationApprove,
    SolicitationDeny,
    SolicitationRegister,
)
from server.models.page_models import PaginationInput
from server.repositories.solicitation_repository import SolicitationRepository
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int
from tests.factories.request.meeting_request_factory import MeetingRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> SolicitationRepositoryAdapter:
    return SolicitationRepositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        session=session,
        user=user,
        permission_index=build_permission_index(user),
    )


def _solicitation_input(
    *,
    building: Building,
    schedule_classroom: Classroom,
    requested_classroom: Classroom | None,
    capacity: int = 10,
    required_classroom: bool = False,
) -> SolicitationRegister:
    base = MeetingRequestFactory(classroom=schedule_classroom).create_input()
    dump = base.model_dump()
    dump["classroom_id"] = requested_classroom.id if requested_classroom else None
    reservation_data = MeetingSolicitation(**dump)
    return SolicitationRegister(
        capacity=capacity,
        required_classroom=required_classroom,
        building_id=must_be_int(building.id),
        reservation_data=reservation_data,
    )


class TestCreate:
    def test_denies_requesting_a_restricted_classroom_without_permission(
        self,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        adapter = _adapter(user=common_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.create(input)

    def test_allows_requesting_a_restricted_classroom_via_role_grant(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.REQUEST],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        solicitation = adapter.create(input)

        assert solicitation.solicited_classroom_id == classroom.id

    def test_allows_requesting_a_restricted_classroom_via_group_membership(
        self,
        restricted_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        adapter = _adapter(user=restricted_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        solicitation = adapter.create(input)

        assert solicitation.solicited_classroom_id == classroom.id

    def test_allows_requesting_an_unrestricted_classroom_without_permission(
        self,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = False
        session.add(classroom)
        session.commit()
        adapter = _adapter(user=common_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        solicitation = adapter.create(input)

        assert solicitation.solicited_classroom_id == classroom.id

    def test_allows_a_solicitation_with_no_requested_classroom_without_permission(
        self,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        adapter = _adapter(user=common_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=None,
        )

        solicitation = adapter.create(input)

        assert solicitation.solicited_classroom_id is None

    def test_admin_always_succeeds_regardless_of_grants(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        adapter = _adapter(user=admin_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        solicitation = adapter.create(input)

        assert solicitation.solicited_classroom_id == classroom.id


class TestUpdate:
    def test_denies_updating_towards_a_restricted_classroom_without_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=common_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=None,
            ),
            session=session,
        )
        session.commit()
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        adapter = _adapter(user=common_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.update(must_be_int(solicitation.id), input)

    def test_allows_updating_towards_a_restricted_classroom_via_role_grant(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=common_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=None,
            ),
            session=session,
        )
        session.commit()
        classroom.restricted = True
        session.add(classroom)
        session.commit()
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.REQUEST],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = _solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        updated = adapter.update(must_be_int(solicitation.id), input)

        assert updated.solicited_classroom_id == classroom.id


class TestCancel:
    def test_owner_can_cancel_their_own_solicitation(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        adapter = _adapter(user=admin_user, session=session)

        cancelled = adapter.cancel(must_be_int(solicitation.id))

        assert cancelled.get_status() == ReservationStatus.CANCELLED


class TestApproveDeny:
    def test_approve_denies_without_reserve_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.approve(
                must_be_int(solicitation.id),
                SolicitationApprove(
                    classroom_id=must_be_int(classroom.id),
                    classroom_name=classroom.name,
                ),
            )

    def test_approve_succeeds_via_reserve_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        approved = adapter.approve(
            must_be_int(solicitation.id),
            SolicitationApprove(
                classroom_id=must_be_int(classroom.id), classroom_name=classroom.name
            ),
        )

        assert approved.get_status() == ReservationStatus.APPROVED

    def test_deny_denies_without_reserve_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.deny(
                must_be_int(solicitation.id),
                SolicitationDeny(justification="Sem vagas disponíveis."),
            )

    def test_deny_succeeds_via_reserve_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        denied = adapter.deny(
            must_be_int(solicitation.id),
            SolicitationDeny(justification="Sem vagas disponíveis."),
        )

        assert denied.get_status() == ReservationStatus.DENIED
        assert denied.denial_justification == "Sem vagas disponíveis."


class TestGetAllAndPending:
    def test_get_all_returns_solicitations_of_owned_buildings(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        adapter = _adapter(user=admin_user, session=session)

        page = adapter.get_all(PaginationInput(page=1, page_size=10))

        assert solicitation.id in [s.id for s in page.items]

    def test_get_pending_returns_pending_solicitations_of_owned_buildings(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()
        adapter = _adapter(user=admin_user, session=session)

        pending = adapter.get_pending()

        assert solicitation.id in [s.id for s in pending]
