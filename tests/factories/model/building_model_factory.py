from sqlmodel import Session
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.dicts.database.building_database_dicts import BuildingModelDict
from tests.factories.model.base_model_factory import BaseModelFactory


class BuildingModelFactory(BaseModelFactory[Building]):
    def __init__(self, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator

    def _get_model_type(self) -> type[Building]:
        return Building

    def get_defaults(self) -> BuildingModelDict:
        return {
            "name": self.faker.company(),
            "created_by_id": self.creator.id,
            "updated_at": self.faker.date_time(),
            "created_by": self.creator,
            "classrooms": [],
            "subjects": [],
            "solicitations": [],
        }
