import pytest
from pydantic import ValidationError

from server.models.http.requests.jupiter_request_models import JupiterLoginRequest


class TestJupiterLoginRequest:
    def test_strips_surrounding_whitespace(self) -> None:
        request = JupiterLoginRequest(n_usp=" 12345678 ", password=" secret ")

        assert request.n_usp == "12345678"
        assert request.password == "secret"

    def test_rejects_an_empty_n_usp(self) -> None:
        with pytest.raises(ValidationError):
            JupiterLoginRequest(n_usp="   ", password="secret")

    def test_rejects_an_empty_password(self) -> None:
        with pytest.raises(ValidationError):
            JupiterLoginRequest(n_usp="12345678", password="   ")
