from sqlmodel import Session
from server.models.database.exam_db_model import Exam
from server.models.database.user_db_model import User
from server.repositories.exam_repository import ExamRepository
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.reservation_permission_checker import (
    ReservationPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction


class ExamPermissionChecker(PermissionChecker[Exam]):
    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user=user, session=session)
        self.reservation_checker = ReservationPermissionChecker(
            self.user, self.session, permission_index
        )

    def check_permission(  # type: ignore[override]
        self, object: int | Exam | list[int] | list[Exam], action: ClassroomAction
    ) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__exam_id_permission_checker(object, action)
        elif isinstance(object, Exam):
            self.__exam_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__exam_list_permission_checker(object, action)

    def __exam_id_permission_checker(self, exam_id: int, action: ClassroomAction) -> None:
        exam = ExamRepository.get_by_id(id=exam_id, session=self.session)
        self.reservation_checker.check_permission(exam.reservation, action)

    def __exam_obj_permission_checker(self, exam: Exam, action: ClassroomAction) -> None:
        self.reservation_checker.check_permission(exam.reservation, action)

    def __exam_list_permission_checker(
        self, exams: list[int] | list[Exam], action: ClassroomAction
    ) -> None:
        for exam in exams:
            if isinstance(exam, int):
                self.__exam_id_permission_checker(exam, action)
            elif isinstance(exam, Exam):
                self.__exam_obj_permission_checker(exam, action)
