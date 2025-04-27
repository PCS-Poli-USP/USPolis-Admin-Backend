from datetime import datetime
from typing import Unpack
from server.models.database.user_db_model import User
from server.models.dicts.database.user_database_dicts import UserModelDict
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

    def create(self, **overrides: Unpack[UserModelDict]) -> User:  # type: ignore
        """Create a user instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[UserModelDict]) -> User:  # type: ignore
        """Create a user instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, user_id: int, **overrides: Unpack[UserModelDict]) -> User:  # type: ignore
        """Create a user instance with default values."""
        return super().update(model_id=user_id, **overrides)
