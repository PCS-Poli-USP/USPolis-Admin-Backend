from datetime import timedelta, UTC

import pytest
from pydantic import ValidationError

from server.models.http.requests.api_key_request_models import (
    ApiClientRegister,
    ApiKeyRateLimitsUpdate,
    RateLimitRegister,
)
from server.utils.brazil_datetime import BrazilDatetime
from tests.factories.request.api_key_request_factory import (
    ApiClientRequestFactory,
    ApiKeyRequestFactory,
)


class TestApiKeyRegister:
    def test_defaults_are_valid(self) -> None:
        payload = ApiKeyRequestFactory().create_input()

        assert payload.allowed_path_prefixes == ["/allocations"]

    def test_duplicate_prefixes_are_collapsed(self) -> None:
        payload = ApiKeyRequestFactory().create_input(
            allowed_path_prefixes=["/allocations", "/allocations"],
        )

        assert payload.allowed_path_prefixes == ["/allocations"]

    @pytest.mark.parametrize(
        "overrides",
        [
            {"allowed_path_prefixes": []},
            {"allowed_path_prefixes": ["/allocations/../admin"]},
            {"expires_at": BrazilDatetime.now_utc() + timedelta(days=2 * 365)},
            {"expires_at": BrazilDatetime.now_utc() - timedelta(minutes=1)},
            {
                "rate_limits": [
                    RateLimitRegister(max_requests=10, window_seconds=60),
                    RateLimitRegister(max_requests=20, window_seconds=60),
                ]
            },
        ],
        ids=[
            "no-prefix",
            "dot-dot-prefix",
            "two-year-expiry",
            "already-expired",
            "duplicate-window",
        ],
    )
    def test_rejects_invalid_payloads(self, overrides: dict) -> None:
        with pytest.raises(ValidationError):
            ApiKeyRequestFactory().create_input(**overrides)

    def test_origins_are_rejected_since_browser_keys_are_gone(self) -> None:
        with pytest.raises(ValidationError, match="navegador"):
            # The field no longer exists: that is what is being tested.
            ApiKeyRequestFactory().create_input(
                allowed_origins=["https://gremio.poli.usp.br"]  # type: ignore[call-arg]
            )

    def test_empty_origins_from_older_clients_are_ignored(self) -> None:
        payload = ApiKeyRequestFactory().create_input(allowed_origins=[])  # type: ignore[call-arg]

        assert not hasattr(payload, "allowed_origins")

    def test_timezone_aware_expiry_is_stored_as_naive_brazil_time(self) -> None:
        in_utc = (
            (BrazilDatetime.now_utc() + timedelta(days=30))
            .replace(tzinfo=BrazilDatetime.brazil_tz())
            .astimezone(UTC)
        )

        payload = ApiKeyRequestFactory().create_input(expires_at=in_utc)

        assert payload.expires_at.tzinfo is None
        assert payload.expires_at == in_utc.astimezone(
            BrazilDatetime.brazil_tz()
        ).replace(tzinfo=None)


class TestRateLimits:
    @pytest.mark.parametrize(
        ("max_requests", "window_seconds"), [(0, 60), (10, 0), (-1, 60)]
    )
    def test_limits_must_be_positive(
        self, max_requests: int, window_seconds: int
    ) -> None:
        with pytest.raises(ValidationError):
            RateLimitRegister(max_requests=max_requests, window_seconds=window_seconds)

    def test_empty_list_means_configured_defaults(self) -> None:
        assert ApiKeyRateLimitsUpdate(rate_limits=[]).rate_limits == []


class TestApiClientRegister:
    def test_defaults_are_valid(self) -> None:
        assert isinstance(ApiClientRequestFactory().create_input(), ApiClientRegister)

    @pytest.mark.parametrize(
        "overrides",
        [{"contact_email": "not-an-email"}, {"contact_name": ""}, {"name": ""}],
    )
    def test_rejects_invalid_contact_or_name(self, overrides: dict) -> None:
        with pytest.raises(ValidationError):
            ApiClientRequestFactory().create_input(**overrides)
