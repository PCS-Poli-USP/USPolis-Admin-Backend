import pytest
from fastapi import HTTPException

from server.utils.type_guard import TypeGuard


class TestMustBeInt:
    def test_returns_the_int_when_not_none(self) -> None:
        assert TypeGuard.must_be_int(42) == 42

    def test_returns_zero_when_input_is_zero(self) -> None:
        assert TypeGuard.must_be_int(0) == 0

    def test_raises_when_input_is_none(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            TypeGuard.must_be_int(None)
        assert exc_info.value.status_code == 500


class TestMustBeStr:
    def test_returns_the_string_when_not_none(self) -> None:
        assert TypeGuard.must_be_str("hello") == "hello"

    def test_returns_empty_string_when_input_is_empty(self) -> None:
        # "" is falsy but not None - must not be treated as "missing".
        assert TypeGuard.must_be_str("") == ""

    def test_raises_when_input_is_none(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            TypeGuard.must_be_str(None)
        assert exc_info.value.status_code == 500


class TestIsNotNone:
    def test_true_when_value_is_not_none(self) -> None:
        assert TypeGuard.is_not_none(0) is True
        assert TypeGuard.is_not_none("") is True
        assert TypeGuard.is_not_none("value") is True

    def test_false_when_value_is_none(self) -> None:
        assert TypeGuard.is_not_none(None) is False


class TestEnsureNotNone:
    def test_returns_the_value_when_not_none(self) -> None:
        assert TypeGuard.ensure_not_none("value") == "value"
        assert TypeGuard.ensure_not_none(0) == 0

    def test_raises_value_error_when_none(self) -> None:
        with pytest.raises(ValueError, match="Value is None"):
            TypeGuard.ensure_not_none(None)
