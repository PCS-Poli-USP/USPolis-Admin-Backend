from typing import Unpack

from sqlmodel import Session

from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_delivery_link_db_model import ApiKeyDeliveryLink
from server.models.database.user_db_model import User
from server.models.dicts.database.api_key_delivery_link_database_dicts import (
    ApiKeyDeliveryLinkModelDict,
)
from server.services.security.api_key_link_crypto import (
    generate_link_id,
    seal_api_key,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from tests.factories.base.api_key_delivery_link_base_factory import (
    ApiKeyDeliveryLinkBaseFactory,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class ApiKeyDeliveryLinkModelFactory(BaseModelFactory[ApiKeyDeliveryLink]):
    """Seals `plaintext` per instance, like the repository does, and keeps
    the token of the last one in `last_token` so tests can open it. Don't
    override `link_id`: it is bound into the ciphertext."""

    def __init__(
        self, api_key: ApiKey, plaintext: str, creator: User, session: Session
    ) -> None:
        super().__init__(session)
        self.api_key = api_key
        self.plaintext = plaintext
        self.creator = creator
        self.core_factory = ApiKeyDeliveryLinkBaseFactory()
        self.last_token: str | None = None

    def _get_model_type(self) -> type[ApiKeyDeliveryLink]:
        return ApiKeyDeliveryLink

    def get_defaults(self) -> ApiKeyDeliveryLinkModelDict:
        core = self.core_factory.get_base_defaults()
        link_id = generate_link_id()
        sealed = seal_api_key(self.plaintext, link_id)
        self.last_token = sealed.token
        return {
            **core,
            "api_key_id": must_be_int(self.api_key.id),
            "link_id": link_id,
            "ciphertext": sealed.ciphertext,
            "nonce": sealed.nonce,
            "salt": sealed.salt,
            "created_by_id": must_be_int(self.creator.id),
            "created_at": BrazilDatetime.now_utc(),
            "consumed_at": None,
            "consumed_ip": None,
            "consumed_user_agent": None,
            "invalidated_at": None,
            "invalidated_by_id": None,
            "emailed_at": None,
            "emailed_to": None,
            "emailed_by_id": None,
        }

    def create(  # type: ignore
        self, **overrides: Unpack[ApiKeyDeliveryLinkModelDict]
    ) -> ApiKeyDeliveryLink:
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[ApiKeyDeliveryLinkModelDict]
    ) -> ApiKeyDeliveryLink:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, link_id: int, **overrides: Unpack[ApiKeyDeliveryLinkModelDict]
    ) -> ApiKeyDeliveryLink:
        return super().update(model_id=link_id, **overrides)
