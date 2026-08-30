import pytest
from fastapi import HTTPException

from server.utils.must_be_int import must_be_int


def test_returns_the_int_when_not_none() -> None:
    assert must_be_int(42) == 42


def test_returns_zero_when_input_is_zero() -> None:
    # 0 is falsy but not None - must not be treated as "missing".
    assert must_be_int(0) == 0


def test_raises_when_input_is_none() -> None:
    with pytest.raises(HTTPException) as exc_info:
        must_be_int(None)
    assert exc_info.value.status_code == 500
