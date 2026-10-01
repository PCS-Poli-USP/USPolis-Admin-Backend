from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.permission_index_dep import PermissionIndexDep
from server.deps.session_dep import SessionDep
from server.models.database.solicitation_db_model import Solicitation
from server.models.http.requests.solicitation_request_models import (
    SolicitationApprove,
    SolicitationDeny,
    SolicitationRegister,
)
from server.models.page_models import Page, PaginationInput
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.solicitation_repository import SolicitationRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.solicitation_permission_checker import (
    SolicitationPermissionChecker,
)
from server.utils.enums.actions_enums import ClassroomAction


class SolicitationRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
        permission_index: PermissionIndexDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.session = session
        self.user = user
        self.classroom_checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.solicitation_checker = SolicitationPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def get_all(self, pagination: PaginationInput) -> Page[Solicitation]:
        return SolicitationRepository.get_by_buildings_ids_paginated(
            building_ids=self.owned_building_ids,
            pagination=pagination,
            session=self.session,
        )

    def get_pending(self) -> list[Solicitation]:
        return SolicitationRepository.get_pending_by_buildings_ids(
            building_ids=self.owned_building_ids, session=self.session
        )

    def __check_restricted_classroom(self, classroom_id: int | None) -> None:
        if classroom_id is None:
            return
        classroom = ClassroomRepository.get_by_id(id=classroom_id, session=self.session)
        if classroom.restricted:
            self.classroom_checker.check_permission(classroom, ClassroomAction.REQUEST)

    def create(self, input: SolicitationRegister) -> Solicitation:
        self.__check_restricted_classroom(input.reservation_data.classroom_id)
        solicitation = SolicitationRepository.create(
            requester=self.user, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(solicitation)
        return solicitation

    def update(self, id: int, input: SolicitationRegister) -> Solicitation:
        self.__check_restricted_classroom(input.reservation_data.classroom_id)
        solicitation = SolicitationRepository.update(
            id=id, input=input, user=self.user, session=self.session
        )
        self.session.commit()
        return solicitation

    def cancel(self, id: int) -> Solicitation:
        solicitation = SolicitationRepository.cancel(
            id=id, user=self.user, session=self.session
        )
        self.session.commit()
        return solicitation

    def approve(self, id: int, input: SolicitationApprove) -> Solicitation:
        self.solicitation_checker.check_permission(id, ClassroomAction.RESERVE)
        solicitation = SolicitationRepository.approve(
            id=id, classroom_id=input.classroom_id, user=self.user, session=self.session
        )
        self.session.refresh(solicitation)
        self.session.commit()
        return solicitation

    def deny(self, id: int, input: SolicitationDeny) -> Solicitation:
        self.solicitation_checker.check_permission(id, ClassroomAction.RESERVE)
        solicitation = SolicitationRepository.deny(
            id=id, input=input, user=self.user, session=self.session
        )
        self.session.commit()
        return solicitation


SolicitationRepositoryDep = Annotated[SolicitationRepositoryAdapter, Depends()]
