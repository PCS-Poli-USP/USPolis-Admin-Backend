from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.dicts.database.building_database_dicts import BuildingModelDict
from tests.factories.model.base_model_factory import BaseModelFactory
from tests.factories.request.building_request_factory import BuildingRequestFactory


class BuildingModelFactory(BaseModelFactory[Building]):
    def __init__(self, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator

    def _get_model_type(self) -> type[Building]:
        return Building

    def get_defaults(self) -> BuildingModelDict:
        base = BuildingRequestFactory().get_default_create()
        return {
            **base,
            "updated_at": datetime.now(),
            "created_by_id": self.creator.id,
            "main_group_id": None,
            "created_by": self.creator,
            "users": [],
            "classrooms": [],
            "subjects": [],
            "solicitations": [],
            "main_group": None,
            "groups": [],
        }

    def create(self, **overrides: Unpack[BuildingModelDict]) -> Building:  # type: ignore
        """Create a building instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[BuildingModelDict]) -> Building:  # type: ignore
        """Create a building instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, building_id: int, **overrides: Unpack[BuildingModelDict]
    ) -> Building:
        """Create a building instance with default values."""
        return super().update(model_id=building_id, **overrides)
