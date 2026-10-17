from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.models.dicts.database.api_key_database_dicts import ApiKeyModelDict
from server.services.security.api_key_crypto import generate_api_key
from server.utils.must_be_int import must_be_int
from tests.factories.base.api_key_base_factory import ApiKeyBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ApiKeyModelFactory(BaseModelFactory[ApiKey]):
    """Generates a real key per instance, like the repository does, and keeps
    the plaintext of the last one in `last_plaintext` so tests can present it."""

    def __init__(self, client: ApiClient, creator: User, session: Session) -> None:
        super().__init__(session)
        self.client = client
        self.creator = creator
        self.core_factory = ApiKeyBaseFactory()
        self.last_plaintext: str | None = None

    def _get_model_type(self) -> type[ApiKey]:
        return ApiKey

    def get_defaults(self) -> ApiKeyModelDict:
        core = self.core_factory.get_base_defaults()
        generated = generate_api_key()
        self.last_plaintext = generated.plaintext
        return {
            **core,
            "client_id": must_be_int(self.client.id),
            "public_id": generated.public_id,
            "key_hash": generated.key_hash,
            "hash_version": generated.hash_version,
            "revoked_at": None,
            "revoked_by_id": None,
            "revoked_reason": None,
            "last_used_at": None,
            "created_by_id": must_be_int(self.creator.id),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "rate_limits": [],
        }

    def create(self, **overrides: Unpack[ApiKeyModelDict]) -> ApiKey:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ApiKeyModelDict]
    ) -> ApiKey:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, api_key_id: int, **overrides: Unpack[ApiKeyModelDict]
    ) -> ApiKey:
        return super().update(model_id=api_key_id, **overrides)
