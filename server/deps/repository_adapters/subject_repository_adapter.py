from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.permission_index_dep import PermissionIndexDep
from server.deps.session_dep import SessionDep
from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from server.repositories.subject_repository import SubjectRepository
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.subjects_permission_checker import (
    SubjectPermissionChecker,
)
from server.utils.enums.actions_enums import BuildingAction


class SubjectRepositoryAdapter:
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
        self.checker = SubjectPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.building_checker = BuildingPermissionChecker(
            user=user,
            session=session,
            permission_index=permission_index,
        )

    def get_by_id(self, id: int) -> Subject:
        subject = SubjectRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(subject, BuildingAction.READ)
        return subject

    def get_all(self) -> list[Subject]:
        return SubjectRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )

    def get_by_code(self, code: str) -> Subject:
        subject = SubjectRepository.get_by_code(code=code, session=self.session)
        self.checker.check_permission(subject, BuildingAction.READ)
        return subject

    def create(self, input: SubjectRegister) -> Subject:
        self.building_checker.check_permission(input.building_ids, BuildingAction.CREATE)
        subject = SubjectRepository.create(input=input, session=self.session)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise SubjectAlreadyExists(input.code)
        self.session.refresh(subject)
        return subject

    def update(self, id: int, input: SubjectUpdate) -> Subject:
        self.checker.check_permission(id, BuildingAction.UPDATE)
        subject = SubjectRepository.update(id=id, input=input, session=self.session)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise SubjectAlreadyExists(input.code)
        return subject

    def delete(self, id: int) -> None:
        # Deleting a Subject ("disciplina") is gated by UPDATE, not DELETE:
        # DELETE is reserved for destroying the Building/Classroom record
        # itself, so this doesn't imply the (far more impactful) ability to
        # delete the physical building.
        subject = SubjectRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(subject, BuildingAction.UPDATE)
        SubjectRepository.delete(id=id, session=self.session)
        self.session.commit()


class SubjectAlreadyExists(HTTPException):
    def __init__(self, subject_code: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A disciplina {subject_code} já existe",
        )


SubjectRepositoryDep = Annotated[SubjectRepositoryAdapter, Depends()]
