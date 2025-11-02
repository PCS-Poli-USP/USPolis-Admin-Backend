from server.models.database.meeting_db_model import Meeting
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)
from tests.utils.validators.reservation.reservation_model_validator import (
    ReservationModelAsserts,
)


class MeetingModelAsserts:
    @staticmethod
    def assert_meeting_after_create(meeting: Meeting, input: MeetingRegister) -> None:
        assert meeting.link == input.link

        reservation = meeting.reservation
        ReservationModelAsserts.assert_reservation_after_create(reservation, input)

    @staticmethod
    def assert_meeting_after_update(meeting: Meeting, input: MeetingUpdate) -> None:
        assert meeting.link == input.link

        reservation = meeting.reservation
        ReservationModelAsserts.assert_reservation_after_update(reservation, input)
