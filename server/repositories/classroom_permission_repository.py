from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_permission_request_models import (
    ClassroomPermissionManyRegister,
    ClassroomPermissionRegister,
    ClassroomPermissionUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.classroom_permission_type_enum import ClassroomPermissionType
from server.utils.must_be_int import must_be_int


class ClassroomPermissionRepository:
    @staticmethod
    def __check_classroom_permissions_validation(
        *,
        classroom_id: int,
        permissions: list[ClassroomPermissionType],
        session: Session,
    ) -> None:
        """Check classroom permissions validation.\n
        A classroom is valid to have permissions when:
        - Classroom is restricted
        - If one permission is RESERVE class must be reservable
        """
        classroom = ClassroomRepository.get_by_id(id=classroom_id, session=session)
        if not classroom.restricted:
            raise InvalidClassroomPermission("A sala permissionada deve ser restrita.")

        if ClassroomPermissionType.RESERVE in permissions and not classroom.restricted:
            raise InvalidClassroomPermission(
                "A sala permissionada não é reservável, apenas permissão de 'Visualizar' é permitido."
            )

    @staticmethod
    def get_all(*, session: Session) -> list[ClassroomPermission]:
        statement = select(ClassroomPermission)
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_id(*, permission_id: int, session: Session) -> ClassroomPermission:
        statement = select(ClassroomPermission).where(
            ClassroomPermission.id == permission_id
        )
        permission = session.exec(statement).first()
        if permission is None:
            raise ClassroomPermissionNotFound(str(permission_id))
        return permission

    @staticmethod
    def get_by_user_id(*, user_id: int, session: Session) -> list[ClassroomPermission]:
        statement = select(ClassroomPermission).where(
            ClassroomPermission.user_id == user_id
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_classroom_id(
        *, classroom_id: int, session: Session
    ) -> list[ClassroomPermission]:
        statement = select(ClassroomPermission).where(
            ClassroomPermission.classroom_id == classroom_id
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_all_by_classroom_ids(
        *, classroom_ids: list[int], session: Session
    ) -> list[ClassroomPermission]:
        statement = select(ClassroomPermission).where(
            col(ClassroomPermission.classroom_id).in_(classroom_ids)
        )
        return list(session.exec(statement).all())

    @staticmethod
    def create(
        *, user: User, input: ClassroomPermissionRegister, session: Session
    ) -> ClassroomPermission:
        ClassroomPermissionRepository.__check_classroom_permissions_validation(
            classroom_id=input.classroom_id,
            permissions=input.permissions,
            session=session,
        )
        permission = ClassroomPermission(
            classroom_id=input.classroom_id,
            user_id=input.user_id,
            given_by_id=must_be_int(user.id),
            permissions=input.permissions,
        )
        session.add(permission)
        return permission

    @staticmethod
    def create_many(
        *, user: User, input: ClassroomPermissionManyRegister, session: Session
    ) -> list[ClassroomPermission]:
        permissions = []
        for data in input.data:
            permission = ClassroomPermissionRepository.create(
                user=user, input=data, session=session
            )
            permissions.append(permission)
        return permissions

    @staticmethod
    def update(
        *,
        user: User,
        permission_id: int,
        input: ClassroomPermissionUpdate,
        session: Session,
    ) -> ClassroomPermission:
        permission = ClassroomPermissionRepository.get_by_id(
            permission_id=permission_id, session=session
        )
        ClassroomPermissionRepository.__check_classroom_permissions_validation(
            classroom_id=permission.classroom_id,
            permissions=input.permissions,
            session=session,
        )
        permission.permissions = input.permissions
        permission.given_by = user
        permission.updated_at = BrazilDatetime.now_utc()
        session.add(permission)
        return permission

    @staticmethod
    def delete(*, permission_id: int, session: Session) -> None:
        permission = ClassroomPermissionRepository.get_by_id(
            permission_id=permission_id, session=session
        )
        session.delete(permission)

    @staticmethod
    def delete_all_by_user_id(*, user_id: int, session: Session) -> None:
        statement = select(ClassroomPermission).where(
            ClassroomPermission.user_id == user_id
        )
        permissions = session.exec(statement).all()
        for permission in permissions:
            session.delete(permission)


class ClassroomPermissionNotFound(HTTPException):
    def __init__(self, permission_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Permissão de sala com {permission_info} não encontrada",
        )


class ClassroomPermissionAlreadyExists(HTTPException):
    def __init__(self, user_id: int, classroom_id: int, permission: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"Permissão '{permission}' para o usuário {user_id} na sala {classroom_id} já existe.",
        )


class InvalidClassroomPermission(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            message,
        )
