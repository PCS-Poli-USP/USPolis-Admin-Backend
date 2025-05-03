from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.models.dicts.database.classroom_database_dicts import ClassroomModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.classroom_base_factory import ClassroomBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ClassroomModelFactory(BaseModelFactory[Classroom]):
    def __init__(self, creator: User, group: Group, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.building = group.building
        self.group = group
        self.core_factory = ClassroomBaseFactory()

    def _get_model_type(self) -> type[Classroom]:
        return Classroom

    def get_defaults(self) -> ClassroomModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "updated_at": datetime.now(),
            "building_id": must_be_int(self.building.id),
            "created_by_id": must_be_int(self.creator.id),
            "created_by": self.creator,
            "building": self.building,
            "schedules": [],
            "occurrences": [],
            "reservations": [],
            "solicitations": [],
            "groups": [self.group],
        }

    def create(self, **overrides: Unpack[ClassroomModelDict]) -> Classroom:  # type: ignore
        """Create a classroom instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[ClassroomModelDict]) -> Classroom:  # type: ignore
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, classroom_id: int, **overrides: Unpack[ClassroomModelDict]
    ) -> Classroom:
        """Create a classroom instance with default values."""
        return super().update(model_id=classroom_id, **overrides)
