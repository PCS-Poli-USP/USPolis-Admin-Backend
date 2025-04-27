from datetime import datetime
from typing import Unpack
from server.models.database.group_db_model import Group
from server.models.dicts.database.group_database_dicts import GroupModelDict
from tests.factories.model.base_model_factory import BaseModelFactory


class GroupModelFactory(BaseModelFactory[Group]):
    def _get_model_type(self) -> type[Group]:
        return Group

    def get_defaults(self) -> GroupModelDict:
        return {
            "name": self.faker.name(),
            "updated_at": datetime.now(),
            "created_at": datetime.now(),
            "classrooms": [],
            "users": [],
        }

    def create(self, **overrides: Unpack[GroupModelDict]) -> Group:  # type: ignore
        """Create a group instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[GroupModelDict]) -> Group:  # type: ignore
        """Create a group instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, group_id: int, **overrides: Unpack[GroupModelDict]) -> Group:  # type: ignore
        """Create a group instance with default values."""
        return super().update(model_id=group_id, **overrides)
