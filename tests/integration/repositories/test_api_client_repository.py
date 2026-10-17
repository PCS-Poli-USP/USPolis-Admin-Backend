import pytest
from sqlalchemy import text
from sqlmodel import Session, select

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.api_key_rate_limit_db_model import ApiKeyRateLimit
from server.models.database.user_db_model import User
from server.repositories.api_client_repository import (
    ApiClientNameAlreadyExists,
    ApiClientNotFound,
    ApiClientRepository,
)
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory
from tests.factories.model.api_key_rate_limit_model_factory import (
    ApiKeyRateLimitModelFactory,
)
from tests.factories.request.api_key_request_factory import ApiClientRequestFactory


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh(name="Grêmio Politécnico")


def test_create_persists_the_client(admin_user: User, session: Session) -> None:
    input = ApiClientRequestFactory().create_input(name="Centro Acadêmico")

    client = ApiClientRepository.create(input=input, user=admin_user, session=session)
    session.commit()
    session.refresh(client)

    assert client.id is not None
    assert client.name == "Centro Acadêmico"
    assert client.contact_email == input.contact_email
    assert client.is_active
    assert client.created_by_id == admin_user.id


@pytest.mark.parametrize("name", ["Grêmio Politécnico", "grêmio politécnico"])
def test_create_rejects_a_taken_name_case_insensitively(
    admin_user: User, session: Session, api_client: ApiClient, name: str
) -> None:
    input = ApiClientRequestFactory().create_input(name=name)

    with pytest.raises(ApiClientNameAlreadyExists):
        ApiClientRepository.create(input=input, user=admin_user, session=session)


def test_update_changes_fields_and_touches_updated_at(
    session: Session, api_client: ApiClient
) -> None:
    before = api_client.updated_at
    input = ApiClientRequestFactory().update_input(
        name="Grêmio Politécnico da USP", contact_name="Nova Diretoria"
    )

    client = ApiClientRepository.update(
        id=api_client.id or 0, input=input, session=session
    )
    session.commit()

    assert client.name == "Grêmio Politécnico da USP"
    assert client.contact_name == "Nova Diretoria"
    assert client.updated_at >= before


def test_update_can_keep_its_own_name_in_another_case(
    session: Session, api_client: ApiClient
) -> None:
    input = ApiClientRequestFactory().update_input(name="GRÊMIO POLITÉCNICO")

    client = ApiClientRepository.update(
        id=api_client.id or 0, input=input, session=session
    )

    assert client.name == "GRÊMIO POLITÉCNICO"


def test_update_rejects_another_clients_name(
    admin_user: User, session: Session, api_client: ApiClient
) -> None:
    other = ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()
    input = ApiClientRequestFactory().update_input(name=api_client.name)

    with pytest.raises(ApiClientNameAlreadyExists):
        ApiClientRepository.update(id=other.id or 0, input=input, session=session)


def test_set_active_toggles_the_kill_switch(
    session: Session, api_client: ApiClient
) -> None:
    ApiClientRepository.set_active(
        id=api_client.id or 0, is_active=False, session=session
    )
    session.commit()
    session.refresh(api_client)
    assert not api_client.is_active

    ApiClientRepository.set_active(
        id=api_client.id or 0, is_active=True, session=session
    )
    session.commit()
    session.refresh(api_client)
    assert api_client.is_active


def test_get_by_id_raises_for_an_unknown_client(session: Session) -> None:
    with pytest.raises(ApiClientNotFound):
        ApiClientRepository.get_by_id(id=999_999, session=session)


def test_get_all_is_ordered_by_name(admin_user: User, session: Session) -> None:
    factory = ApiClientModelFactory(creator=admin_user, session=session)
    for name in ["Zeta", "Alfa", "Meio"]:
        factory.create(name=name)
    session.commit()

    names = [c.name for c in ApiClientRepository.get_all(session=session)]

    assert names == ["Alfa", "Meio", "Zeta"]


class TestDeleteCascades:
    """Deleting a client removes its keys and their rate limits, both through
    the ORM and directly in the database."""

    def seed(self, admin_user: User, session: Session, client: ApiClient) -> int:
        key = ApiKeyModelFactory(
            client=client, creator=admin_user, session=session
        ).create_and_refresh()
        ApiKeyRateLimitModelFactory(api_key=key, session=session).create_and_refresh()
        return key.id or 0

    def assert_gone(self, session: Session, key_id: int) -> None:
        session.expire_all()
        assert session.get(ApiKey, key_id) is None
        limits = session.exec(
            select(ApiKeyRateLimit).where(ApiKeyRateLimit.api_key_id == key_id)
        ).all()
        assert limits == []

    def test_through_the_orm(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> None:
        key_id = self.seed(admin_user, session, api_client)

        session.delete(api_client)
        session.commit()

        self.assert_gone(session, key_id)

    def test_in_the_database(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> None:
        key_id = self.seed(admin_user, session, api_client)

        session.exec(  # type: ignore[call-overload]
            text("DELETE FROM apiclient WHERE id = :id"), params={"id": api_client.id}
        )
        session.commit()

        self.assert_gone(session, key_id)
