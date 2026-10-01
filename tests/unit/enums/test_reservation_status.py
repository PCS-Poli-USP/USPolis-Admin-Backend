from server.utils.enums.reservation_status import ReservationStatus


def test_values_returns_every_member() -> None:
    assert set(ReservationStatus.values()) == set(ReservationStatus)


def test_get_status_detail_returns_a_message_for_every_status() -> None:
    for status in ReservationStatus:
        detail = ReservationStatus.get_status_detail(status)
        assert detail != "Status desconhecido."


def test_get_status_detail_falls_back_for_unknown_status() -> None:
    assert (
        ReservationStatus.get_status_detail("not-a-real-status")  # type: ignore[arg-type]
        == "Status desconhecido."
    )
