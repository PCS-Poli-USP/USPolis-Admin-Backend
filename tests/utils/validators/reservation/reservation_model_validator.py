from server.models.database.reservation_db_model import Reservation
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.utils.enums.reservation_status import ReservationStatus
from tests.utils.validators.schedule.schedule_model_validator import (
    ScheduleModelAsserts,
)


class ReservationModelAsserts:
    @staticmethod
    def assert_reservation_after_create(
        reservation: Reservation, input: ReservationRegister
    ) -> None:
        assert reservation.title == input.title
        assert reservation.type == input.type
        assert reservation.reason == input.reason
        assert reservation.status == ReservationStatus.APPROVED

        schedule = reservation.schedule
        ScheduleModelAsserts.assert_schedule_after_create(schedule, input.schedule_data)

    @staticmethod
    def assert_reservation_after_update(
        reservation: Reservation, input: ReservationUpdate
    ) -> None:
        assert reservation.title == input.title
        assert reservation.type == input.type
        assert reservation.reason == input.reason
        assert reservation.status == ReservationStatus.APPROVED

        schedule = reservation.schedule
        ScheduleModelAsserts.assert_schedule_after_update(schedule, input.schedule_data)
