from datetime import datetime
from typing import Unpack

from sqlmodel import Session
from server.models.database.user_db_model import User
from server.models.dicts.database.user_database_dicts import UserModelDict
from tests.factories.base.user_base_factory import UserBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class UserModelFactory(BaseModelFactory[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.core_factory = UserBaseFactory()

    def _get_model_type(self) -> type[User]:
        return User

    def get_defaults(self) -> UserModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "name": self.core_factory.get_random_name(),
            "email": self.core_factory.get_random_email(),
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

    def create_many_and_refresh(  # type: ignore
        self,
        count: int = BaseModelFactory.CREATE_MANY_DEFAULT_COUNT,
        **overrides: Unpack[UserModelDict],
    ) -> list[User]:
        """Create many user instances with default values and refresh them."""
        return super().create_many_and_refresh(count=count, **overrides)

    def update(self, user_id: int, **overrides: Unpack[UserModelDict]) -> User:  # type: ignore
        """Create a user instance with default values."""
        return super().update(model_id=user_id, **overrides)
