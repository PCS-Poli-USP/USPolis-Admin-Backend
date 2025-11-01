from server.models.database.exam_db_model import Exam
from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate
from tests.utils.validators.reservation.reservation_model_validator import (
    ReservationModelAsserts,
)


class ExamModelAsserts:
    @staticmethod
    def assert_exam_after_create(exam: Exam, input: ExamRegister) -> None:
        reservation = exam.reservation
        ReservationModelAsserts.assert_reservation_after_create(reservation, input)

        assert exam.subject_id == input.subject_id
        assert len(exam.classes) == len(input.class_ids)
        exam_class_ids = {cls.id for cls in exam.classes}
        input_class_ids = set(input.class_ids)
        assert exam_class_ids == input_class_ids

    @staticmethod
    def assert_exam_after_update(exam: Exam, input: ExamUpdate) -> None:
        reservation = exam.reservation
        ReservationModelAsserts.assert_reservation_after_update(reservation, input)

        assert exam.subject_id == input.subject_id
        assert len(exam.classes) == len(input.class_ids)
        exam_class_ids = {cls.id for cls in exam.classes}
        input_class_ids = set(input.class_ids)
        assert exam_class_ids == input_class_ids
