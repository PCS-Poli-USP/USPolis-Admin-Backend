from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.http.requests.classroom_permission_request_models import (
    ClassroomPermissionManyRegister,
    ClassroomPermissionRegister,
    ClassroomPermissionUpdate,
)
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)


class ClassroomPermissionRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
    ) -> None:
        self.session = session
        self.user = user
        self.owned_building_ids = owned_building_ids
        self.classroom_checker = ClassroomPermissionChecker(user=user, session=session)

    def get_all(self) -> list[ClassroomPermission]:
        classroom_ids = self.user.classrooms_ids()
        return ClassroomPermissionRepository.get_all_by_classroom_ids(
            classroom_ids=classroom_ids, session=self.session
        )

    def create(self, input: ClassroomPermissionRegister) -> ClassroomPermission:
        self.classroom_checker.check_permission(input.classroom_id)
        try:
            permission = ClassroomPermissionRepository.create(
                user=self.user, input=input, session=self.session
            )
        except IntegrityError:
            raise ClassroomPermissionAlreadyExists()
        self.session.commit()
        self.session.refresh(permission)
        return permission

    def create_many(
        self, input: ClassroomPermissionManyRegister
    ) -> list[ClassroomPermission]:
        classrooms_ids = [data.classroom_id for data in input.data]
        self.classroom_checker.check_permission(classrooms_ids)
        try:
            permissions = ClassroomPermissionRepository.create_many(
                user=self.user, input=input, session=self.session
            )
        except IntegrityError:
            raise ClassroomPermissionManyAlreadyExists()

        self.session.commit()
        for permission in permissions:
            self.session.refresh(permission)

        return permissions

    def update(self, id: int, input: ClassroomPermissionUpdate) -> ClassroomPermission:
        permission = ClassroomPermissionRepository.get_by_id(
            permission_id=id, session=self.session
        )
        self.classroom_checker.check_permission(permission.classroom)
        permission = ClassroomPermissionRepository.update(
            user=self.user, permission_id=id, input=input, session=self.session
        )
        self.session.commit()
        return permission

    def delete(self, id: int) -> None:
        permission = ClassroomPermissionRepository.get_by_id(
            permission_id=id, session=self.session
        )
        self.classroom_checker.check_permission(permission.classroom_id)
        ClassroomPermissionRepository.delete(permission_id=id, session=self.session)
        self.session.commit()


class ClassroomPermissionAlreadyExists(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="O usuário já tem permissão para a sala informada",
        )


class ClassroomPermissionManyAlreadyExists(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Um ou mais usuários já tem as permissões fornecidas",
        )


ClassroomPermissionRepositoryDep = Annotated[
    ClassroomPermissionRepositoryAdapter, Depends()
]
