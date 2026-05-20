from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from sqlmodel import Session, select

from server.models.database.base_permission_db_model import BasePermission
from server.models.database.user_db_model import User
from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.type_guard import TypeGuard

P = TypeVar("P", bound=BasePermission)
A = TypeVar("A")


class PermissionRepository(Generic[P, A]):
    """Generic repository for permission models with a resource id and action."""

    model: type[P] | None = None
    resource_field: str | None = None

    @classmethod
    def get_by_id(cls, *, id: int, session: Session) -> P:
        model = TypeGuard.ensure_not_none(cls.model)
        statement = select(model).where(model.id == id)
        permission = session.exec(statement).first()
        if permission is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Permissão não encontrada")
        return permission

    @classmethod
    def get_all(cls, *, session: Session) -> list[P]:
        model = TypeGuard.ensure_not_none(cls.model)
        statement = select(model)
        return list(session.exec(statement).all())

    @classmethod
    def get_all_by_role_id(cls, *, role_id: int, session: Session) -> list[P]:
        model = TypeGuard.ensure_not_none(cls.model)
        statement = select(model).where(model.role_id == role_id)
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
        resource_id = getattr(input, resource_field)

        payload: dict[str, Any] = {
            resource_field: resource_id,
            "actions": input.actions,
            "user_id": input.user_id,
            "role_id": input.role_id,
            "granted_by": TypeGuard.must_be_int(user.id),
        }
        permission = model(**payload)
        session.add(permission)
        return permission

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
        if not hasattr(input, resource_field):
            raise ValueError("PermissionRepository input is missing resource field")

        resource_id = getattr(input, resource_field)
        setattr(permission, resource_field, resource_id)
        permission.actions = input.actions
        permission.user_id = input.user_id
        permission.role_id = input.role_id
        permission.granted_by = TypeGuard.must_be_int(user.id)
        session.add(permission)
        return permission

    @classmethod
    def delete(cls, *, id: int, session: Session) -> None:
        permission = cls.get_by_id(id=id, session=session)
        session.delete(permission)
