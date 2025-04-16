from datetime import datetime
from server.models.database.user_db_model import User
from server.models.dicts.database.user_database_dicts import UserModelDict
from server.models.dicts.requests.user_requests_dicts import (
    UserRegisterDict,
    UserUpdateDict,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class UserModelFactory(BaseModelFactory[User]):
    def _get_model_type(self) -> type[User]:
        return User

    def get_defaults(self) -> UserModelDict:
        return {
            "name": self.faker.name(),
            "email": self.faker.email(domain="usp.br"),
            "is_admin": False,
            "updated_at": datetime.now(),
            "last_visited": datetime.now(),
            "created_by_id": None,
            "created_by": None,
            "buildings": [],
            "holidays_categories": [],
            "holidays": [],
            "calendars": [],
            "reservations": [],
            "solicitations": [],
            "groups": [],
        }

    def create(self, **overrides: UserRegisterDict) -> User:
        """Create a user instance with default values."""
        return super().create(**overrides)

    def update(self, id: int, **overrides: UserUpdateDict) -> User:
        """Create a user instance with default values."""
        return super().update(id, **overrides)
