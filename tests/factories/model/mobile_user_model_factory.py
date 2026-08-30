from typing import Unpack

from sqlmodel import Session

from server.models.database.mobile_user_db_model import MobileUser
from server.models.dicts.database.mobile_user_database_dicts import MobileUserModelDict
from tests.factories.base.mobile_user_base_factory import MobileUserBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class MobileUserModelFactory(BaseModelFactory[MobileUser]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.core_factory = MobileUserBaseFactory()

    def _get_model_type(self) -> type[MobileUser]:
        return MobileUser

    def get_defaults(self) -> MobileUserModelDict:
        core = self.core_factory.get_base_defaults()
        return {**core}

    def create(self, **overrides: Unpack[MobileUserModelDict]) -> MobileUser:  # type: ignore
        """Create a mobile user instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[MobileUserModelDict]
    ) -> MobileUser:
        """Create a mobile user instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, mobile_user_id: int, **overrides: Unpack[MobileUserModelDict]) -> MobileUser:  # type: ignore
        """Update a mobile user instance with default values."""
        return super().update(model_id=mobile_user_id, **overrides)
