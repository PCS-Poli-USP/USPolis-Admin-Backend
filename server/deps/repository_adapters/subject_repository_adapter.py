from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
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


class SubjectRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.session = session
        self.user = user
        self.checker = SubjectPermissionChecker(user=user, session=session)
        self.building_checker = BuildingPermissionChecker(
            user=user,
            session=session,
        )

    def get_by_id(self, id: int) -> Subject:
        subject = SubjectRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(object=subject)
        return subject

    def get_all(self) -> list[Subject]:
        return SubjectRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )

    def get_by_code(self, code: str) -> Subject:
        subject = SubjectRepository.get_by_code(code=code, session=self.session)
        self.checker.check_permission(object=subject)
        return subject

    def create(self, input: SubjectRegister) -> Subject:
        self.building_checker.check_permission(input.building_ids)
        subject = SubjectRepository.create(input=input, session=self.session)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise SubjectAlreadyExists(input.code)
        self.session.refresh(subject)
        return subject

    def update(self, id: int, input: SubjectUpdate) -> Subject:
        self.checker.check_permission(object=id)
        subject = SubjectRepository.update(id=id, input=input, session=self.session)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise SubjectAlreadyExists(input.code)
        return subject

    def delete(self, id: int) -> None:
        subject = SubjectRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(object=subject)
        SubjectRepository.delete(id=id, session=self.session)
        self.session.commit()


class SubjectAlreadyExists(HTTPException):
    def __init__(self, subject_code: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A disciplina {subject_code} já existe",
        )


SubjectRepositoryDep = Annotated[SubjectRepositoryAdapter, Depends()]
