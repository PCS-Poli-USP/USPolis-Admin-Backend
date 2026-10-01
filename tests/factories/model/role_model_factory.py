from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.role_db_model import Role
from server.models.dicts.database.role_database_dicts import RoleModelDict
from server.utils.enums.resources_enums import Resource
from tests.factories.base.role_base_factory import RoleBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class RoleModelFactory(BaseModelFactory[Role]):
    def __init__(
        self, session: Session, resources: list[Resource] | None = None
    ) -> None:
        super().__init__(session)
        self.core_factory = RoleBaseFactory(resources=resources)

    def _get_model_type(self) -> type[Role]:
        return Role

    def get_defaults(self) -> RoleModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "users": [],
        }

    def create(self, **overrides: Unpack[RoleModelDict]) -> Role:  # type: ignore
        """Create a role instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[RoleModelDict]) -> Role:  # type: ignore
        """Create a role instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, role_id: int, **overrides: Unpack[RoleModelDict]) -> Role:  # type: ignore
        """Update a role instance with default values."""
        role = super().update(role_id, **overrides)
        role.updated_at = datetime.now()
        return role
