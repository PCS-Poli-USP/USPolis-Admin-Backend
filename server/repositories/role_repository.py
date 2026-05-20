from typing import cast

from fastapi import HTTPException, status
from sqlmodel import Session, select

from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.models.http.requests.permission_request_models import PermissionRegister
from server.models.http.requests.role_request_models import RoleRegister
from server.models.http.requests.role_request_models import RoleUpdate
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.repositories.course_permission_repository import CoursePermissionRepository
from server.utils.enums.resources_enums import Resource
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.permissions_types import Permission


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
        user: User,
        session: Session,
    ) -> Role:
        """Create a role instance using a request model.\n
        The role is created first to ensure it has a valid ID for linking permissions.\n
        Permissions are then created and linked to the role based on the provided permission registers and IDs.
        """
        role = Role(
            name=input.name,
            description=input.description,
            resources=input.resources,
        )
        session.add(role)
        session.flush()
        role_id = cls.__ensure_role_id(role)

        existing_permissions: dict[Resource, list[Permission]] = (
            cls.__permissions_from_ids(
                permission_ids=input.permissions_ids or [],
                session=session,
            )
        )
        new_permissions = cls.__normalize_permissions(
            new_permissions=input.permissions,
            existing_permissions=existing_permissions,
        )
        cls.__create_permissions(
            role_id=role_id,
            permissions=new_permissions,
            user=user,
            session=session,
        )
        return role

    @classmethod
    def update(
        cls,
        *,
        id: int,
        input: RoleUpdate,
        user: User,
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

        new_permissions = cls.__normalize_permissions(
            new_permissions=input.permissions,
            existing_permissions=existing_permissions,
        )
        desired_permission_signatures = {
            cls.__permission_signature(permission) for permission in desired_permissions
        }

        permissions_to_remove = [
            permission
            for permission in current_permissions
            if cls.__permission_signature(permission)
            not in desired_permission_signatures
        ]
        permissions_to_create = [
            permission
            for permission in desired_permissions
            if cls.__permission_signature(permission)
            not in previous_permission_signatures
        ]

        if permissions_to_remove or permissions_to_create:
            for permission in permissions_to_remove:
                session.delete(permission)
            cls.__create_permissions(
                role_id=role_id,
                permissions=permissions_to_create,
                user=user,
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
    def __create_permissions(
        cls,
        *,
        role_id: int,
        permissions: list[PermissionRegister],
        user: User,
        session: Session,
    ) -> None:
        """Create permissions for a role based on the provided permission registers.\n
        For each permission register, a new permission instance is created and linked to the role.\n
        If a permission register references an existing permission by ID, that permission is duplicated and linked to
        """
        for permission in permissions:
            repository = ROLE_PERMISSION_REPOSITORY_MAP[permission.resource]
            permission_input = permission.model_copy(
                update={"role_id": role_id, "user_id": None}
            )
            created_permission = repository.create(
                input=permission_input,
                user=user,
                session=session,
            )
            session.refresh(created_permission)

    @classmethod
    def __normalize_permissions(
        cls,
        *,
        new_permissions: list[PermissionRegister] | None,
        existing_permissions: dict[Resource, list[Permission]],
    ) -> list[PermissionRegister]:
        """
        Normalize permissions from both explicit definitions and existing IDs, ensuring uniqueness.\n
        For permissions provided as IDs, the corresponding permission are fetched for deduplicate the register list.\n
        The final list of permissions is deduplicated based on resource, actions, and resource ID
        """
        normalized_permissions: list[PermissionRegister] = []
        if new_permissions:
            normalized_permissions.extend(new_permissions)

        unique_permissions: dict[tuple, PermissionRegister] = {}
        for permission in normalized_permissions:
            key = (
                permission.resource,
                cls.__action_signature(permission.actions),
                permission.resource_id,
            )
            unique_permissions[key] = permission

        for r, p in existing_permissions.items():
            for data in p:
                existing_key = (
                    r,
                    cls.__action_signature(list(data.actions)),
                    cls.__resource_id_for_permission(data, r),
                )
                if existing_key in unique_permissions:
                    unique_permissions.pop(existing_key)

        return list(unique_permissions.values())

    @classmethod
    def __permissions_from_ids(
        cls,
        *,
        permission_ids: list[tuple[int, Resource]],
        session: Session,
    ) -> dict[Resource, list[Permission]]:
        """Fetch permissions based on provided IDs and group them by resource type."""
        permissions_map: dict[Resource, list[Permission]] = {}
        for permission_id, resource in permission_ids:
            permission = cls.__get_permission_by_id(
                permission_id=permission_id,
                resource=resource,
                session=session,
            )
            if permission.role_id is not None:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Permissão já vinculada a um cargo",
                )
            if permission.user_id is None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Permissão sem alvo associado, estado inválido",
                )

            resource_id = cls.__resource_id_for_permission(permission, resource)
            if resource_id is None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Permissão não possui recurso associado",
                )

            if resource not in permissions_map:
                permissions_map[resource] = []
            permissions_map[resource].append(permission)
        return permissions_map

    @classmethod
    def __get_permission_by_id(
        cls,
        *,
        permission_id: int,
        resource: Resource,
        session: Session,
    ) -> Permission:
        """Fetch a permission instance based on its ID and resource type."""
        repository = ROLE_PERMISSION_REPOSITORY_MAP[resource]
        return repository.get_by_id(id=permission_id, session=session)

    @staticmethod
    def __resource_id_for_permission(
        permission: Permission,
        resource: Resource,
    ) -> int | None:
        """Extract the resource ID from a permission instance based on its resource type."""
        if resource == Resource.CLASSROOM:
            classroom_permission = cast(ClassroomPermission, permission)
            return classroom_permission.classroom_id
        if resource == Resource.COURSE:
            course_permission = cast(CoursePermission, permission)
            return course_permission.course_id

    @classmethod
    def __delete_permissions(
        cls,
        *,
        role_id: int,
        resources: list[Resource],
        session: Session,
    ) -> None:
        """Delete permissions linked to a role for the specified resources."""
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
    ) -> list[Permission]:
        """Fetch current permissions linked to a role for the specified resources."""
        permissions: list[Permission] = []
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
        """Merge current and desired resources, ensuring uniqueness while preserving order."""
        merged_resources: list[Resource] = []
        for resource in [*current_resources, *desired_resources]:
            if resource not in merged_resources:
                merged_resources.append(resource)
        return merged_resources

    @classmethod
    def __permission_signature(cls, permission: object) -> tuple:
        """Create a signature for a permission based on its resource, actions, and resource ID to ensure uniqueness."""
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
            cls.__action_signature(getattr(permission, "actions")),
            resource_id,
            getattr(permission, "user_id", None),
            getattr(permission, "role_id", None),
            getattr(permission, "granted_by", None),
        )

    @staticmethod
    def __action_signature(actions: list) -> tuple:
        """Create a signature for a list of actions, ensuring that the order of actions does not affect the signature."""
        return tuple(sorted(str(action) for action in actions))

    @staticmethod
    def __ensure_role_id(role: Role) -> int:
        """Ensure that the role instance has a valid ID, which is necessary for linking permissions."""
        if role.id is None:
            raise ValueError("Role must be persisted before handling permissions")
        return role.id


class RoleNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Cargo com id {id} não encontrado")
