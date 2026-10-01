from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.models.http.requests.permission_request_models import PermissionRegister
from server.models.http.requests.role_request_models import RoleRegister
from server.models.http.requests.role_request_models import RoleUpdate

from server.repositories.building_permission_repository import (
    BuildingPermissionRepository,
)
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.repositories.course_permission_repository import CoursePermissionRepository
from server.repositories.user_repository import UserRepository

from server.utils.enums.resources_enums import Resource
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from server.utils.permissions_types import Permission


ROLE_PERMISSION_REPOSITORY_MAP: dict[
    Resource,
    type[
        BuildingPermissionRepository
        | ClassroomPermissionRepository
        | CoursePermissionRepository
    ],
] = {
    Resource.BUILDING: BuildingPermissionRepository,
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
    def get_all(cls, *, session: Session, resources: list[Resource] = []) -> list[Role]:
        statement = select(Role)
        if resources:
            statement = statement.where(col(Role.resources).op("&&")(resources))
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
        Permissions are then created and linked to the role based on the provided permission registers.
        """
        role = Role(
            name=input.name,
            description=input.description,
            resources=input.resources,
        )
        session.add(role)
        session.flush()
        role_id = cls.__ensure_role_id(role)

        new_permissions = cls.__deduplicate_permissions(input.permissions)
        cls.__create_permissions(
            role_id=role_id,
            permissions=new_permissions,
            user=user,
            session=session,
        )
        cls.__sync_users(
            role_id=role_id,
            user_ids=input.user_ids,
            granted_by=user,
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

        current_permissions = cls.__current_permissions(
            role_id=role_id,
            resources=role.resources,
            session=session,
        )
        desired_permissions = cls.__deduplicate_permissions(input.permissions)
        desired_signatures = {
            cls.__permission_signature(permission) for permission in desired_permissions
        }
        current_signatures = {
            cls.__permission_signature(permission) for permission in current_permissions
        }

        permissions_to_remove = [
            permission
            for permission in current_permissions
            if cls.__permission_signature(permission) not in desired_signatures
        ]
        permissions_to_create = [
            permission
            for permission in desired_permissions
            if cls.__permission_signature(permission) not in current_signatures
        ]

        role.name = input.name
        role.description = input.description
        role.resources = input.resources

        for permission in permissions_to_remove:
            session.delete(permission)

        cls.__create_permissions(
            role_id=role_id,
            permissions=permissions_to_create,
            user=user,
            session=session,
        )
        cls.__sync_users(
            role_id=role_id,
            user_ids=input.user_ids,
            granted_by=user,
            session=session,
        )

        role.updated_at = BrazilDatetime.now_utc()
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
    def add_user(
        cls, *, role_id: int, user_id: int, granted_by: User, session: Session
    ) -> Role:
        """Grant a single user this role. Raises `UserAlreadyInRole` (409) if the
        user already holds it - commits internally to catch that conflict."""
        role = cls.get_by_id(id=role_id, session=session)
        user = UserRepository.get_by_id(user_id=user_id, session=session)
        session.add(
            UserRole(
                user_id=must_be_int(user.id),
                role_id=role_id,
                granted_by_id=must_be_int(granted_by.id),
            )
        )
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise UserAlreadyInRole(role_name=role.name, user_name=user.name)
        session.refresh(role)
        return role

    @classmethod
    def remove_user(cls, *, role_id: int, user_id: int, session: Session) -> Role:
        role = cls.get_by_id(id=role_id, session=session)
        link = session.exec(
            select(UserRole).where(
                UserRole.role_id == role_id, UserRole.user_id == user_id
            )
        ).first()
        if link is None:
            user = UserRepository.get_by_id(user_id=user_id, session=session)
            raise UserNotInRole(role_name=role.name, user_name=user.name)
        session.delete(link)
        return role

    @classmethod
    def __sync_users(
        cls,
        *,
        role_id: int,
        user_ids: list[int],
        granted_by: User,
        session: Session,
    ) -> None:
        """Sync a role's user assignments to match `user_ids` exactly: creates
        UserRole links for newly added ids and deletes links for removed ones.
        `UserRole` carries a required `granted_by_id`, so - unlike a bare link
        table - it can't be synced via plain relationship assignment."""
        current_links = list(
            session.exec(select(UserRole).where(UserRole.role_id == role_id)).all()
        )
        current_user_ids = {link.user_id for link in current_links}
        desired_user_ids = set(user_ids)

        for link in current_links:
            if link.user_id not in desired_user_ids:
                session.delete(link)

        ids_to_add = desired_user_ids - current_user_ids
        if not ids_to_add:
            return
        users_to_add = UserRepository.get_by_ids(ids=list(ids_to_add), session=session)
        for user in users_to_add:
            session.add(
                UserRole(
                    user_id=must_be_int(user.id),
                    role_id=role_id,
                    granted_by_id=must_be_int(granted_by.id),
                )
            )

    @classmethod
    def __create_permissions(
        cls,
        *,
        role_id: int,
        permissions: list[PermissionRegister],
        user: User,
        session: Session,
    ) -> None:
        """Create permissions for a role based on the provided permission registers."""
        for permission in permissions:
            repository = ROLE_PERMISSION_REPOSITORY_MAP[permission.resource]
            permission_input = permission.model_copy(update={"role_id": role_id})
            created_permission = repository.create(
                input=permission_input,
                user=user,
                session=session,
            )
            session.flush()
            session.refresh(created_permission)

    @classmethod
    def __deduplicate_permissions(
        cls,
        permissions: list[PermissionRegister] | None,
    ) -> list[PermissionRegister]:
        """Deduplicate permission registers based on resource, actions, and resource ID."""
        unique_permissions: dict[tuple, PermissionRegister] = {}
        for permission in permissions or []:
            key = (
                permission.resource,
                cls.__action_signature(permission.actions),
                permission.resource_id,
            )
            unique_permissions[key] = permission
        return list(unique_permissions.values())

    @classmethod
    def __delete_permissions(
        cls,
        *,
        role_id: int,
        resources: list[Resource],
        session: Session,
    ) -> None:
        """Delete all permissions linked to a role for the specified resources."""
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
    def __permission_signature(
        cls, permission: Permission | PermissionRegister
    ) -> tuple[Resource, tuple, int | None]:
        """Create a signature for a permission based on its resource, actions, and resource ID to ensure uniqueness."""
        resource: Resource | None = getattr(permission, "resource", None)
        if resource is None:
            if isinstance(permission, ClassroomPermission):
                resource = Resource.CLASSROOM
            elif isinstance(permission, CoursePermission):
                resource = Resource.COURSE
            elif isinstance(permission, BuildingPermission):
                resource = Resource.BUILDING
        if resource is None:
            raise ValueError("Permission without resource is invalid")

        resource_id: int | None = getattr(permission, "resource_id", None)
        if resource_id is None:
            if isinstance(permission, ClassroomPermission):
                resource_id = permission.classroom_id
            elif isinstance(permission, CoursePermission):
                resource_id = permission.course_id
            elif isinstance(permission, BuildingPermission):
                resource_id = permission.building_id
        if resource_id == -1:
            # -1 (request-side "all instances") and None (DB-side wildcard) are the
            # same wildcard scope and must compare equal, or an unchanged wildcard
            # permission looks different on every update and gets deleted+recreated.
            resource_id = None

        return (
            resource,
            cls.__action_signature(getattr(permission, "actions")),
            resource_id,
        )

    @staticmethod
    def __action_signature(actions: list) -> tuple[str, ...]:
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


class UserAlreadyInRole(HTTPException):
    def __init__(self, *, role_name: str, user_name: str) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            f"Usuário {user_name} já possui o cargo {role_name}",
        )


class UserNotInRole(HTTPException):
    def __init__(self, *, role_name: str, user_name: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Usuário {user_name} não possui o cargo {role_name}",
        )
