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

    def test_duplicate_prefixes_and_origins_are_collapsed(self) -> None:
        payload = ApiKeyRequestFactory().create_input(
            allowed_path_prefixes=["/allocations", "/allocations"],
            allowed_origins=["https://site.com", "https://SITE.com/"],
        )

        assert payload.allowed_path_prefixes == ["/allocations"]
        assert payload.allowed_origins == ["https://site.com"]

    @pytest.mark.parametrize(
        "overrides",
        [
            {"allowed_path_prefixes": []},
            {"allowed_path_prefixes": ["/allocations/../admin"]},
            {"allowed_origins": ["https://*.usp.br"]},
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
            "wildcard-origin",
            "two-year-expiry",
            "already-expired",
            "duplicate-window",
        ],
    )
    def test_rejects_invalid_payloads(self, overrides: dict) -> None:
        with pytest.raises(ValidationError):
            ApiKeyRequestFactory().create_input(**overrides)

    def test_http_origin_is_rejected_in_production(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "server.models.http.requests.api_key_request_models.CONFIG.environment",
            "production",
        )

        with pytest.raises(ValidationError):
            ApiKeyRequestFactory().create_input(
                allowed_origins=["http://localhost:3000"]
            )

    def test_http_localhost_origin_is_allowed_outside_production(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "server.models.http.requests.api_key_request_models.CONFIG.environment",
            "development",
        )

        payload = ApiKeyRequestFactory().create_input(
            allowed_origins=["http://localhost:3000"]
        )
        assert payload.allowed_origins == ["http://localhost:3000"]

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
