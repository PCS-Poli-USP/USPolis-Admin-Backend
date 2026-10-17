from datetime import timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from server.models.database.api_client_db_model import ApiClient
from server.models.database.api_key_db_model import ApiKey
from server.models.database.user_db_model import User
from server.models.http.requests.api_key_request_models import RateLimitRegister
from server.repositories.api_key_repository import (
    ApiKeyAlreadyRevoked,
    ApiKeyNotFound,
    ApiKeyRepository,
)
from server.services.rate_limiter import RateLimitRule
from server.services.security.api_key_crypto import parse_api_key, verify_api_key
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.model.api_client_model_factory import ApiClientModelFactory
from tests.factories.model.api_key_model_factory import ApiKeyModelFactory
from tests.factories.model.api_key_rate_limit_model_factory import (
    ApiKeyRateLimitModelFactory,
)
from tests.factories.request.api_key_request_factory import ApiKeyRequestFactory


@pytest.fixture
def api_client(admin_user: User, session: Session) -> ApiClient:
    return ApiClientModelFactory(
        creator=admin_user, session=session
    ).create_and_refresh()


@pytest.fixture
def api_key(admin_user: User, session: Session, api_client: ApiClient) -> ApiKey:
    return ApiKeyModelFactory(
        client=api_client, creator=admin_user, session=session
    ).create_and_refresh()


def limits(*pairs: tuple[int, int]) -> list[RateLimitRegister]:
    return [RateLimitRegister(max_requests=m, window_seconds=w) for m, w in pairs]


class TestCreate:
    def test_returns_a_plaintext_that_verifies_against_the_stored_hash(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> None:
        input = ApiKeyRequestFactory().create_input()

        key, plaintext = ApiKeyRepository.create(
            client_id=api_client.id or 0, input=input, user=admin_user, session=session
        )
        session.commit()
        session.refresh(key)

        assert parse_api_key(plaintext) == key.public_id
        assert verify_api_key(plaintext, key.key_hash, key.hash_version)
        assert key.created_by_id == admin_user.id
        assert key.revoked_at is None

    def test_plaintext_is_never_persisted(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> None:
        key, plaintext = ApiKeyRepository.create(
            client_id=api_client.id or 0,
            input=ApiKeyRequestFactory().create_input(),
            user=admin_user,
            session=session,
        )
        session.commit()
        secret_part = plaintext.split("_")[3]

        row = session.exec(  # type: ignore[call-overload]
            text("SELECT * FROM apikey WHERE id = :id"), params={"id": key.id}
        ).one()
        stored = " ".join(str(value) for value in row)
        assert plaintext not in stored
        assert secret_part not in stored

    def test_creates_its_rate_limits(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> None:
        input = ApiKeyRequestFactory().create_input(
            rate_limits=limits((30, 10), (120, 60))
        )

        key, _ = ApiKeyRepository.create(
            client_id=api_client.id or 0, input=input, user=admin_user, session=session
        )
        session.commit()
        session.refresh(key)

        assert [r.to_rule() for r in key.rate_limits] == [
            RateLimitRule(30, 10),
            RateLimitRule(120, 60),
        ]


class TestLookup:
    def test_get_by_public_id_loads_client_and_rate_limits(
        self, session: Session, api_key: ApiKey
    ) -> None:
        ApiKeyRateLimitModelFactory(
            api_key=api_key, session=session
        ).create_and_refresh()
        session.expire_all()

        found = ApiKeyRepository.get_by_public_id(
            public_id=api_key.public_id, session=session
        )

        assert found is not None and found.id == api_key.id
        assert found.client.is_active
        assert len(found.rate_limits) == 1

    def test_get_by_public_id_returns_none_for_an_unknown_key(
        self, session: Session
    ) -> None:
        assert (
            ApiKeyRepository.get_by_public_id(
                public_id="0123456789abcdef", session=session
            )
            is None
        )

    def test_get_by_id_raises_for_an_unknown_key(self, session: Session) -> None:
        with pytest.raises(ApiKeyNotFound):
            ApiKeyRepository.get_by_id(id=999_999, session=session)

    def test_get_all_by_client_only_returns_that_clients_keys(
        self, admin_user: User, session: Session, api_client: ApiClient, api_key: ApiKey
    ) -> None:
        other_client = ApiClientModelFactory(
            creator=admin_user, session=session
        ).create_and_refresh()
        ApiKeyModelFactory(
            client=other_client, creator=admin_user, session=session
        ).create_and_refresh()

        keys = ApiKeyRepository.get_all_by_client(
            client_id=api_client.id or 0, session=session
        )

        assert [k.id for k in keys] == [api_key.id]


class TestUpdate:
    def test_changes_scope_and_expiry(self, session: Session, api_key: ApiKey) -> None:
        input = ApiKeyRequestFactory().update_input(
            allowed_path_prefixes=["/allocations", "/buildings"],
            allowed_origins=["https://gremio.poli.usp.br"],
        )

        key = ApiKeyRepository.update(id=api_key.id or 0, input=input, session=session)
        session.commit()
        session.refresh(key)

        assert key.allowed_path_prefixes == ["/allocations", "/buildings"]
        assert key.is_browser_key
        assert key.expires_at == input.expires_at

    def test_set_rate_limits_replaces_them_even_when_a_window_is_kept(
        self, session: Session, api_key: ApiKey
    ) -> None:
        ApiKeyRepository.set_rate_limits(
            id=api_key.id or 0, limits=limits((10, 60), (500, 3600)), session=session
        )
        session.commit()

        # Same 60s window with a new max: must not hit the unique constraint.
        key = ApiKeyRepository.set_rate_limits(
            id=api_key.id or 0, limits=limits((20, 60)), session=session
        )
        session.commit()
        session.refresh(key)

        assert [r.to_rule() for r in key.rate_limits] == [RateLimitRule(20, 60)]

    def test_set_rate_limits_with_an_empty_list_clears_them(
        self, session: Session, api_key: ApiKey
    ) -> None:
        ApiKeyRateLimitModelFactory(
            api_key=api_key, session=session
        ).create_and_refresh()

        key = ApiKeyRepository.set_rate_limits(
            id=api_key.id or 0, limits=[], session=session
        )
        session.commit()
        session.refresh(key)

        assert key.rate_limits == []


class TestRevoke:
    def test_records_who_when_and_why(
        self, admin_user: User, session: Session, api_key: ApiKey
    ) -> None:
        key = ApiKeyRepository.revoke(
            id=api_key.id or 0,
            reason="Vazou no GitHub",
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(key)

        assert key.revoked_at is not None
        assert key.revoked_by_id == admin_user.id
        assert key.revoked_reason == "Vazou no GitHub"
        assert not key.is_usable()

    def test_revoking_twice_is_a_conflict(
        self, admin_user: User, session: Session, api_key: ApiKey
    ) -> None:
        ApiKeyRepository.revoke(
            id=api_key.id or 0, reason="motivo", user=admin_user, session=session
        )
        session.commit()

        with pytest.raises(ApiKeyAlreadyRevoked) as error:
            ApiKeyRepository.revoke(
                id=api_key.id or 0, reason="de novo", user=admin_user, session=session
            )
        assert error.value.status_code == 409

    def test_a_revoked_key_can_no_longer_be_changed(
        self, admin_user: User, session: Session, api_key: ApiKey
    ) -> None:
        ApiKeyRepository.revoke(
            id=api_key.id or 0, reason="motivo", user=admin_user, session=session
        )
        session.commit()

        with pytest.raises(ApiKeyAlreadyRevoked):
            ApiKeyRepository.update(
                id=api_key.id or 0,
                input=ApiKeyRequestFactory().update_input(),
                session=session,
            )
        with pytest.raises(ApiKeyAlreadyRevoked):
            ApiKeyRepository.set_rate_limits(
                id=api_key.id or 0, limits=limits((1, 1)), session=session
            )


class TestDatabaseConstraints:
    """The CHECK/UNIQUE constraints hold even if code bypasses the request
    validators."""

    @pytest.fixture
    def factory(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> ApiKeyModelFactory:
        return ApiKeyModelFactory(
            client=api_client, creator=admin_user, session=session
        )

    def assert_rejected(self, session: Session, constraint: str) -> None:
        with pytest.raises(IntegrityError, match=constraint):
            session.commit()
        session.rollback()

    def test_a_key_needs_at_least_one_path_prefix(
        self, session: Session, factory: ApiKeyModelFactory
    ) -> None:
        factory.create(allowed_path_prefixes=[])
        self.assert_rejected(session, "api_key_check_has_path_prefix")

    def test_revoked_by_requires_revoked_at(
        self, admin_user: User, session: Session, factory: ApiKeyModelFactory
    ) -> None:
        factory.create(revoked_by_id=admin_user.id, revoked_at=None)
        self.assert_rejected(session, "api_key_check_revoked_by_requires_revoked_at")

    def test_revoked_at_without_revoked_by_is_allowed(
        self, session: Session, factory: ApiKeyModelFactory
    ) -> None:
        # e.g. revoked by an automatic job, or the revoking admin was deleted.
        key = factory.create_and_refresh(revoked_at=BrazilDatetime.now_utc())

        assert key.revoked_by_id is None

    def test_expiry_must_be_after_creation(
        self, session: Session, factory: ApiKeyModelFactory
    ) -> None:
        now = BrazilDatetime.now_utc()
        factory.create(created_at=now, expires_at=now - timedelta(seconds=1))
        self.assert_rejected(session, "api_key_check_expires_after_created")

    def test_public_id_is_unique(
        self, session: Session, factory: ApiKeyModelFactory, api_key: ApiKey
    ) -> None:
        factory.create(public_id=api_key.public_id)
        self.assert_rejected(session, "ix_apikey_public_id")

    def test_a_window_appears_once_per_key(
        self, session: Session, api_key: ApiKey
    ) -> None:
        rate_limits = ApiKeyRateLimitModelFactory(api_key=api_key, session=session)
        rate_limits.create(window_seconds=60)
        rate_limits.create(window_seconds=60)
        self.assert_rejected(session, "unique_api_key_rate_limit_window")

    @pytest.mark.parametrize(
        ("overrides", "constraint"),
        [
            ({"max_requests": 0}, "max_requests_positive"),
            ({"window_seconds": 0}, "window_seconds_positive"),
        ],
    )
    def test_rate_limit_values_must_be_positive(
        self, session: Session, api_key: ApiKey, overrides: dict, constraint: str
    ) -> None:
        ApiKeyRateLimitModelFactory(api_key=api_key, session=session).create(
            **overrides
        )
        self.assert_rejected(session, constraint)


class TestActiveBrowserOrigins:
    def test_only_usable_browser_keys_count(
        self, admin_user: User, session: Session, api_client: ApiClient
    ) -> None:
        factory = ApiKeyModelFactory(
            client=api_client, creator=admin_user, session=session
        )
        now = BrazilDatetime.now_utc()
        factory.create_and_refresh(allowed_origins=["https://ativo.usp.br"])
        factory.create_and_refresh(allowed_origins=[])  # server key
        factory.create_and_refresh(
            allowed_origins=["https://revogado.usp.br"], revoked_at=now
        )
        factory.create_and_refresh(
            allowed_origins=["https://expirado.usp.br"],
            created_at=now - timedelta(days=10),
            expires_at=now - timedelta(days=1),
        )
        inactive = ApiClientModelFactory(
            creator=admin_user, session=session
        ).create_and_refresh(is_active=False)
        ApiKeyModelFactory(
            client=inactive, creator=admin_user, session=session
        ).create_and_refresh(allowed_origins=["https://inativo.usp.br"])

        origins = ApiKeyRepository.get_active_browser_origins(session=session)

        assert origins == {"https://ativo.usp.br"}
