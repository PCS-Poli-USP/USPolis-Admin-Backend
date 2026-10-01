from server.models.http.responses.institutional_event_response_models import (
    InstitutionalAllocationEventResponse,
)
from tests.utils.institutional_event_test_utils import make_institutional_event


class TestInstitutionalAllocationEventResponse:
    def test_from_institutional_event(self) -> None:
        event = make_institutional_event(
            title="Semana da Computação",
            location="Auditório",
            building="Bloco A",
            classroom="Sala 1",
            external_link="https://example.com",
            likes=5,
        )

        data = InstitutionalAllocationEventResponse.from_institutional_event(event)

        assert data.id == event.id
        assert data.title == "Semana da Computação"
        assert data.location == "Auditório"
        assert data.building == "Bloco A"
        assert data.classroom == "Sala 1"
        assert data.external_link == "https://example.com"
        assert data.likes == 5

    def test_from_institutional_event_list(self) -> None:
        event1 = make_institutional_event()
        event2 = make_institutional_event()

        data = InstitutionalAllocationEventResponse.from_institutional_event_list(
            [event1, event2]
        )

        assert [d.id for d in data] == [event1.id, event2.id]
