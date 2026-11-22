import pytest

from server.repositories.search_query_log_repository import is_loggable_query
from server.repositories.search_repository import (
    build_prefix_tsquery,
    normalize_query,
)


def test_normalize_query_strips_accents_case_and_extra_spaces() -> None:
    assert normalize_query("  Cálculo   Diferencial  ") == "calculo diferencial"


def test_normalize_query_folds_crawler_mojibake_accents() -> None:
    # The crawler stores some names as "Jordăo" (ă instead of ã).
    assert normalize_query("Jordăo") == "jordao"


def test_build_prefix_tsquery_ands_tokens_and_prefixes_the_last() -> None:
    assert build_prefix_tsquery("Cálculo Dif") == "calculo & dif:*"


def test_build_prefix_tsquery_single_token() -> None:
    assert build_prefix_tsquery("MAC0110") == "mac0110:*"


def test_build_prefix_tsquery_splits_codes_with_punctuation() -> None:
    assert build_prefix_tsquery("B2-04") == "b2 & 04:*"


def test_build_prefix_tsquery_drops_tsquery_operators_from_input() -> None:
    assert build_prefix_tsquery("a & b | !c <-> (d):*") == "a & b & c & d:*"


def test_build_prefix_tsquery_returns_empty_when_nothing_is_searchable() -> None:
    assert build_prefix_tsquery("  !!! & | ") == ""


@pytest.mark.parametrize(
    "query",
    ["calculo", "mac0110", "0303200", "b2-04", "monitoria pea3306", "sala 2026"],
)
def test_regular_queries_are_loggable(query: str) -> None:
    assert is_loggable_query(query)


@pytest.mark.parametrize(
    "query",
    [
        "fulano@usp.br",
        "12345678",
        "123.456.789-00",
        "(11) 99999-1234",
        "nusp 1234 5678",
    ],
)
def test_personal_data_is_not_loggable(query: str) -> None:
    assert not is_loggable_query(query)
