from fastapi import HTTPException, status
from sqlmodel import Session
from server.models.database.exam_db_model import Exam
from server.models.database.user_db_model import User
from server.repositories.exam_repository import ExamRepository
from server.services.security.base_permission_checker import PermissionChecker


class ExamPermissionChecker(PermissionChecker[Exam]):
    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(self, object: int | Exam | list[int] | list[Exam]) -> None:
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__exam_id_permission_checker(object)
        elif isinstance(object, Exam):
            self.__exam_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__exam_list_permission_checker(object)

    def __exam_id_permission_checker(self, exam_id: int) -> None:
        exam = ExamRepository.get_by_id(id=exam_id, session=self.session)
        self.__exam_obj_permission_checker(exam)

    def __exam_obj_permission_checker(self, exam: Exam) -> None:
        classroom = exam.reservation.classroom
        if classroom.id not in self.user.classrooms_ids_set():
            raise ForbiddenExamAccess("You do not have permission to access this exam.")

    def __exam_list_permission_checker(self, exams: list[int] | list[Exam]) -> None:
        for exam in exams:
            if isinstance(exam, int):
                self.__exam_id_permission_checker(exam)
            elif isinstance(exam, Exam):
                self.__exam_obj_permission_checker(exam)


class ForbiddenExamAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
