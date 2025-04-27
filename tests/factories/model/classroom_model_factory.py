from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.dicts.database.classroom_database_dicts import ClassroomModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.model.base_model_factory import BaseModelFactory
from tests.factories.request.classroom_request_factory import ClassroomRequestFactory


class ClassroomModelFactory(BaseModelFactory[Classroom]):
    def __init__(self, creator: User, building: Building, session: Session) -> None:
        super().__init__(session)
        self.building = building
        self.creator = creator

    def _get_model_type(self) -> type[Classroom]:
        return Classroom

    def get_defaults(self) -> ClassroomModelDict:
        core = ClassroomRequestFactory(self.building).get_default_register_input()
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
