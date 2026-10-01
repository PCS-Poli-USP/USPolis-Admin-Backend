import pytest

from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.mobile_institutional_event_response_models import (
    MobileInstitutionalAllocationEventResponse,
    to_event_update,
)
from tests.utils.institutional_event_test_utils import make_institutional_event


class TestMobileInstitutionalAllocationEventResponse:
    def test_from_model(self) -> None:
        event = make_institutional_event(
            title="Semana da Computação", building="Bloco A", likes=3
        )

        data = MobileInstitutionalAllocationEventResponse.from_model(event)

        assert data.id == event.id
        assert data.title == "Semana da Computação"
        assert data.building == "Bloco A"
        assert data.likes == 3

    def test_raises_when_event_has_no_id(self) -> None:
        event = make_institutional_event()
        event.id = None

        with pytest.raises(UnfetchDataError):
            MobileInstitutionalAllocationEventResponse.from_model(event)

    def test_from_institutional_event_list(self) -> None:
        event1 = make_institutional_event()
        event2 = make_institutional_event()

        data = MobileInstitutionalAllocationEventResponse.from_institutional_event_list(
            [event1, event2]
        )

        assert [d.id for d in data] == [event1.id, event2.id]


class TestToEventUpdate:
    def test_maps_every_field(self) -> None:
        event = make_institutional_event(
            title="Semana da Computação",
            description="Evento anual",
            category="Palestra",
            building="Bloco A",
            classroom="Sala 1",
            location="Auditório",
            external_link="https://example.com",
        )

        update = to_event_update(event)

        assert update.title == "Semana da Computação"
        assert update.description == "Evento anual"
        assert update.category == "Palestra"
        assert update.building == "Bloco A"
        assert update.classroom == "Sala 1"
        assert update.location == "Auditório"
        assert update.external_link == "https://example.com"
