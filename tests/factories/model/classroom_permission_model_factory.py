from typing import Unpack

from sqlmodel import Session

from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.dicts.database.classroom_permission_database_dicts import (
    ClassroomPermissionModelDict,
)
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.factories.base.permission_base_factory import PermissionBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ClassroomPermissionModelFactory(BaseModelFactory[ClassroomPermission]):
    def __init__(self, role: Role, granted_by: User, session: Session) -> None:
        super().__init__(session)
        self.role = role
        self.granted_by = granted_by
        self.core_factory = PermissionBaseFactory(
            role_id=must_be_int(role.id), resource=Resource.CLASSROOM
        )

    def _get_model_type(self) -> type[ClassroomPermission]:
        return ClassroomPermission

    def get_defaults(self) -> ClassroomPermissionModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            "classroom_id": None if core["resource_id"] == -1 else core["resource_id"],  # type: ignore
            "actions": core["actions"],  # type: ignore
            "role_id": core["role_id"],  # type: ignore
            "granted_by_id": must_be_int(self.granted_by.id),
        }

    def create(  # type: ignore
        self,
        **overrides: Unpack[ClassroomPermissionModelDict],
    ) -> ClassroomPermission:
        """Create a classroom permission instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ClassroomPermissionModelDict]
    ) -> ClassroomPermission:
        """Create a classroom permission instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)
