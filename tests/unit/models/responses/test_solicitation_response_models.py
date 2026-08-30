from server.models.http.responses.solicitation_response_models import (
    SolicitationResponse,
)
from server.utils.enums.reservation_status import ReservationStatus
from tests.utils.academic_test_utils import (
    make_building,
    make_reservation,
    make_solicitation,
    make_user,
)
from tests.utils.time_test_utils import make_schedule


class TestSolicitationResponse:
    def test_from_solicitation(self) -> None:
        building = make_building(name="Bloco A")
        user = make_user()
        solicitation = make_solicitation(building=building, user=user, capacity=25)
        schedule = make_schedule(classroom=None)
        schedule.occurrences = []
        schedule.logs = []
        reservation = make_reservation(schedule=schedule, solicitation=solicitation)
        solicitation.reservation = reservation

        data = SolicitationResponse.from_solicitation(solicitation)

        assert data.id == solicitation.id
        assert data.capacity == 25
        assert data.status == ReservationStatus.APPROVED
        assert data.building == "Bloco A"
        assert data.user == user.name
        assert data.email == user.email
        assert data.reservation.id == reservation.id

    def test_from_solicitation_list(self) -> None:
        building = make_building()
        user = make_user()
        solicitation1 = make_solicitation(building=building, user=user)
        schedule1 = make_schedule(classroom=None)
        schedule1.occurrences = []
        schedule1.logs = []
        reservation1 = make_reservation(schedule=schedule1, solicitation=solicitation1)
        solicitation1.reservation = reservation1

        solicitation2 = make_solicitation(building=building, user=user)
        schedule2 = make_schedule(classroom=None)
        schedule2.occurrences = []
        schedule2.logs = []
        reservation2 = make_reservation(schedule=schedule2, solicitation=solicitation2)
        solicitation2.reservation = reservation2

        data = SolicitationResponse.from_solicitation_list([solicitation1, solicitation2])

        assert [d.id for d in data] == [solicitation1.id, solicitation2.id]
