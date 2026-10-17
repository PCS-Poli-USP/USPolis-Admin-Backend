from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.user_db_model import User
from server.models.dicts.database.api_client_database_dicts import ApiClientModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.api_client_base_factory import ApiClientBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ApiClientModelFactory(BaseModelFactory[ApiClient]):
    def __init__(self, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.core_factory = ApiClientBaseFactory()

    def _get_model_type(self) -> type[ApiClient]:
        return ApiClient

    def get_defaults(self) -> ApiClientModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "is_active": True,
            "created_by_id": must_be_int(self.creator.id),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def create(self, **overrides: Unpack[ApiClientModelDict]) -> ApiClient:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ApiClientModelDict]
    ) -> ApiClient:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, api_client_id: int, **overrides: Unpack[ApiClientModelDict]
    ) -> ApiClient:
        return super().update(model_id=api_client_id, **overrides)
