from server.models.database.meeting_db_model import Meeting
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.reservation_type import ReservationType


class MeetingModelAsserts:
    @staticmethod
    def assert_meeting_after_create(meeting: Meeting, input: MeetingRegister) -> None:
        reservation = meeting.reservation
        schedule = reservation.schedule

        assert meeting.link == input.link

        assert reservation.title == input.title
        assert reservation.type == ReservationType.MEETING
        assert reservation.reason == input.reason

        assert reservation.status == ReservationStatus.APPROVED

    @staticmethod
    def assert_meeting_after_update(meeting: Meeting, input: MeetingUpdate) -> None:
        reservation = meeting.reservation
        schedule = reservation.schedule

        assert meeting.link == input.link

        assert reservation.title == input.title
        assert reservation.type == ReservationType.MEETING
        assert reservation.reason == input.reason

        assert reservation.status == ReservationStatus.APPROVED
