from datetime import datetime
from typing import Unpack

from sqlmodel import Session
from server.models.database.building_db_model import Building
from server.models.database.group_db_model import Group
from server.models.dicts.database.group_database_dicts import GroupModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.group_base_factory import GroupBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class GroupModelFactory(BaseModelFactory[Group]):
    def __init__(self, building: Building, session: Session) -> None:
        super().__init__(session)
        self.building = building
        self.core_factory = GroupBaseFactory(must_be_int(building.id))

    def _get_model_type(self) -> type[Group]:
        return Group

    def get_defaults(self) -> GroupModelDict:
        core = self.core_factory.get_base_defaults()

        return {
            **core,
            "updated_at": datetime.now(),
            "created_at": datetime.now(),
            "classrooms": [],
            "users": [],
        }

    def create(self, **overrides: Unpack[GroupModelDict]) -> Group:  # type: ignore
        """Create a group instance with default values.\n
        A default group is a group without classrooms with a random name
        """
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[GroupModelDict]) -> Group:  # type: ignore
        """Create a group instance with default values, commit and refresh it.\n
        A default group is a group without classrooms with a random name
        """
        return super().create_and_refresh(**overrides)

    def update(self, group_id: int, **overrides: Unpack[GroupModelDict]) -> Group:  # type: ignore
        """Create a group instance with default values."""
        return super().update(model_id=group_id, **overrides)
