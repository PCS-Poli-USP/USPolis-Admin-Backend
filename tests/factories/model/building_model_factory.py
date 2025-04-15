from datetime import datetime
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
        core = BuildingRequestFactory().get_default_create()
        return {
            **core,
            "updated_at": datetime.now(),
            "created_by_id": self.creator.id,
            "created_by": self.creator,
            "classrooms": [],
            "subjects": [],
            "solicitations": [],
        }

    def create(self, **overrides: BuildingModelDict) -> Building:
        """Create a building instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: BuildingModelDict) -> Building:
        """Create a building instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, id: int, **overrides: BuildingModelDict) -> Building:
        """Create a building instance with default values."""
        return super().update(id, **overrides)
