from fastapi import HTTPException, status
from sqlmodel import Session, select

from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.role_db_model import Role
from server.models.database.user_role_db_model import UserRole
from server.models.http.requests.role_request_models import RoleRegister
from server.models.http.requests.role_request_models import RoleUpdate
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.repositories.course_permission_repository import CoursePermissionRepository
from server.utils.enums.resources_enums import Resource
from server.utils.brazil_datetime import BrazilDatetime


ROLE_PERMISSION_REPOSITORY_MAP: dict[
    Resource, type[ClassroomPermissionRepository | CoursePermissionRepository]
] = {
    Resource.CLASSROOM: ClassroomPermissionRepository,
    Resource.COURSE: CoursePermissionRepository,
}


class RoleRepository:
    @classmethod
    def get_by_id(cls, *, id: int, session: Session) -> Role:
        statement = select(Role).where(Role.id == id)
        role = session.exec(statement).first()
        if role is None:
            raise RoleNotFound(id=id)
        return role

    @classmethod
    def get_all(cls, *, session: Session) -> list[Role]:
        statement = select(Role)
        return list(session.exec(statement).all())

    @classmethod
    def create(
        cls,
        *,
        input: RoleRegister,
        session: Session,
    ) -> Role:
        """Create a role instance using a request model."""
        role = Role(
            name=input.name,
            description=input.description,
            resources=input.resources,
        )
        session.add(role)
        session.flush()
        role_id = cls.__ensure_role_id(role)

        cls.__replace_permissions(
            role_id=role_id,
            permissions=input.permissions,
            session=session,
        )
        return role

    @classmethod
    def update(
        cls,
        *,
        id: int,
        input: RoleUpdate,
        session: Session,
    ) -> Role:
        role = cls.get_by_id(id=id, session=session)
        role_id = cls.__ensure_role_id(role)
        resources_to_consider = cls.__merge_resources(
            current_resources=role.resources,
            desired_resources=input.resources,
        )
        current_permissions = cls.__current_permissions(
            role_id=role_id,
            resources=resources_to_consider,
            session=session,
        )
        previous_permission_signatures = {
            cls.__permission_signature(permission) for permission in current_permissions
        }

        role.name = input.name
        role.description = input.description
        role.resources = input.resources

        desired_permission_signatures = {
            cls.__permission_signature(permission) for permission in input.permissions
        }

        permissions_to_remove = [
            permission
            for permission in current_permissions
            if cls.__permission_signature(permission)
            not in desired_permission_signatures
        ]
        permissions_to_create = [
            permission
            for permission in input.permissions
            if cls.__permission_signature(permission)
            not in previous_permission_signatures
        ]

        if permissions_to_remove or permissions_to_create:
            for permission in permissions_to_remove:
                session.delete(permission)
            cls.__replace_permissions(
                role_id=role_id,
                permissions=permissions_to_create,
                session=session,
            )

        role.updated_at = BrazilDatetime.now_utc()
        session.add(role)
        return role

    @classmethod
    def delete(cls, *, id: int, session: Session) -> None:
        role = cls.get_by_id(id=id, session=session)
        role_id = cls.__ensure_role_id(role)

        cls.__delete_permissions(
            role_id=role_id,
            resources=role.resources,
            session=session,
        )
        role_links = list(
            session.exec(select(UserRole).where(UserRole.role_id == role_id)).all()
        )

        for link in role_links:
            session.delete(link)

        session.delete(role)

    @classmethod
    def __replace_permissions(
        cls,
        *,
        role_id: int,
        permissions: list,
        session: Session,
    ) -> None:
        for permission in permissions:
            repository = ROLE_PERMISSION_REPOSITORY_MAP[permission.resource]
            permission_input = permission.model_copy(update={"role_id": role_id})
            created_permission = repository.create(
                input=permission_input,
                session=session,
            )
            session.refresh(created_permission)

    @classmethod
    def __delete_permissions(
        cls,
        *,
        role_id: int,
        resources: list[Resource],
        session: Session,
    ) -> None:
        for resource in resources:
            repository = ROLE_PERMISSION_REPOSITORY_MAP[resource]
            for permission in repository.get_all_by_role_id(
                role_id=role_id,
                session=session,
            ):
                session.delete(permission)

    @classmethod
    def __current_permissions(
        cls,
        *,
        role_id: int,
        resources: list[Resource],
        session: Session,
    ) -> list:
        permissions: list = []
        for resource in resources:
            repository = ROLE_PERMISSION_REPOSITORY_MAP[resource]
            permissions.extend(
                repository.get_all_by_role_id(role_id=role_id, session=session)
            )
        return permissions

    @classmethod
    def __merge_resources(
        cls,
        *,
        current_resources: list[Resource],
        desired_resources: list[Resource],
    ) -> list[Resource]:
        merged_resources: list[Resource] = []
        for resource in [*current_resources, *desired_resources]:
            if resource not in merged_resources:
                merged_resources.append(resource)
        return merged_resources

    @staticmethod
    def __permission_signature(permission: object) -> tuple:
        resource = getattr(permission, "resource", None)
        if resource is None:
            if isinstance(permission, ClassroomPermission):
                resource = Resource.CLASSROOM
            elif isinstance(permission, CoursePermission):
                resource = Resource.COURSE

        resource_id = getattr(permission, "resource_id", None)
        if resource_id is None:
            if isinstance(permission, ClassroomPermission):
                resource_id = permission.classroom_id
            elif isinstance(permission, CoursePermission):
                resource_id = permission.course_id

        return (
            resource,
            getattr(permission, "action"),
            resource_id,
            getattr(permission, "user_id", None),
            getattr(permission, "role_id", None),
            getattr(permission, "granted_by", None),
        )

    @staticmethod
    def __ensure_role_id(role: Role) -> int:
        if role.id is None:
            raise ValueError("Role must be persisted before handling permissions")
        return role.id


class RoleNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Cargo com id {id} não encontrado")
