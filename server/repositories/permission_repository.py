from typing import Any, Generic, TypeVar, cast

from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from server.models.database.base_permission_db_model import BasePermission
from server.models.database.user_db_model import User
from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.type_guard import TypeGuard


P = TypeVar("P", bound=BasePermission)
A = TypeVar("A")


class PermissionRepository(Generic[P, A]):
    """Generic repository for permission models with a resource id and action."""

    model: type[P] | None = None
    resource_field: str | None = None

    @staticmethod
    def _normalize_resource_id(resource_id: int | None) -> int | None:
        if resource_id == -1:
            return None
        return resource_id

    @staticmethod
    def _with_role(statement: Any, model: type[P]) -> Any:
        model_any = cast(Any, model)
        return statement.options(selectinload(model_any.role))

    @classmethod
    def get_by_id(cls, *, id: int, session: Session) -> P:
        model = TypeGuard.ensure_not_none(cls.model)
        statement = select(model).where(model.id == id)
        statement = cls._with_role(statement, model)
        permission = session.exec(statement).first()
        if permission is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Permissão não encontrada")
        return permission  # type: ignore

    @classmethod
    def get_all(cls, *, session: Session) -> list[P]:
        model = TypeGuard.ensure_not_none(cls.model)
        statement = cls._with_role(select(model), model)
        return list(session.exec(statement).all())

    @classmethod
    def get_all_by_role_id(cls, *, role_id: int, session: Session) -> list[P]:
        model = TypeGuard.ensure_not_none(cls.model)
        statement = cls._with_role(
            select(model).where(model.role_id == role_id), model
        )
        return list(session.exec(statement).all())

    @classmethod
    def get_by_ids(cls, *, resource_ids: list[int], session: Session) -> list[P]:
        """Get every permission scoped to any of `resource_ids` (matched
        against this subclass's `resource_field`, e.g. `building_id` or
        `classroom_id`). Used to clean up permissions left dangling when
        their resource is deleted - those FKs have no ON DELETE CASCADE."""
        model = TypeGuard.ensure_not_none(cls.model)
        resource_field = TypeGuard.ensure_not_none(cls.resource_field)
        column = getattr(model, resource_field)
        statement = select(model).where(column.in_(resource_ids))
        return list(session.exec(statement).all())

    @classmethod
    def create(
        cls,
        *,
        input: PermissionRegister,
        user: User,
        session: Session,
    ) -> P:
        """Create a permission instance using a request model."""
        model = TypeGuard.ensure_not_none(cls.model)
        resource_field = TypeGuard.ensure_not_none(cls.resource_field)
        resource_id = cls._normalize_resource_id(input.resource_id)

        payload: dict[str, Any] = {
            resource_field: resource_id,
            "actions": input.actions,
            "role_id": input.role_id,
            "granted_by_id": TypeGuard.must_be_int(user.id),
        }
        permission = model(**payload)

        from server.repositories.role_repository import RoleRepository

        role = RoleRepository.get_by_id(id=input.role_id, session=session)
        role.extend_resource(input.resource)
        role.updated_at = BrazilDatetime.now_utc()
        session.add(role)

        session.add(permission)
        return permission

    @classmethod
    def create_batch(
        cls,
        *,
        inputs: list[PermissionRegister],
        user: User,
        session: Session,
    ) -> list[P]:
        """Create multiple permission instances using a list of request models."""
        permissions: list[P] = []
        for input in inputs:
            permission = cls.create(input=input, user=user, session=session)
            permissions.append(permission)
        return permissions

    @classmethod
    def update(
        cls,
        *,
        permission: P,
        input: PermissionUpdate,
        user: User,
        session: Session,
    ) -> P:
        """Update a permission instance with new values."""
        resource_field = TypeGuard.ensure_not_none(cls.resource_field)
        resource_id = cls._normalize_resource_id(input.resource_id)
        setattr(permission, resource_field, resource_id)
        permission.actions = input.actions
        permission.role_id = input.role_id
        permission.granted_by_id = TypeGuard.must_be_int(user.id)
        session.add(permission)
        return permission

    @classmethod
    def delete(cls, *, id: int, session: Session) -> None:
        permission = cls.get_by_id(id=id, session=session)
        session.delete(permission)
