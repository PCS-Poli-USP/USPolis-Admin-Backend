from server.utils.enums.recurrence import Recurrence


def test_to_string_returns_the_raw_value() -> None:
    assert Recurrence.WEEKLY.to_string() == "Weekly"


def test_translated_returns_a_portuguese_label_for_every_member() -> None:
    for recurrence in Recurrence:
        assert recurrence.translated() != "Desconhecido"


def test_values_returns_every_member() -> None:
    assert set(Recurrence.values()) == set(Recurrence)
