from typing import Annotated

from fastapi import Depends
from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.database.exam_db_model import Exam
from server.models.database.user_db_model import User
from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.exam_repository import ExamRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.exam_permission_checker import ExamPermissionChecker


class ExamRepositoryAdapter:
    def __init__(self, user: UserDep, session: SessionDep):
        self.session = session
        self.user = user
        self.checker = ExamPermissionChecker(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(user=user, session=session)

    def get_by_id(self, id: int) -> Exam:
        exam = ExamRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(exam)
        return exam

    def create(self, creator: User, input: ExamRegister) -> Exam:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.classroom_checker.check_permission(classroom)
        exam = ExamRepository.create(creator=creator, input=input, session=self.session)
        self.session.commit()
        self.session.refresh(exam)
        return exam

    def update(self, id: int, input: ExamUpdate) -> Exam:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.classroom_checker.check_permission(classroom)
        exam = ExamRepository.update(
            user=self.user, id=id, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(exam)
        return exam

    def delete(self, id: int) -> None:
        exam = ExamRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(exam)
        ExamRepository.delete(id=id, session=self.session)
        self.session.commit()


ExamRepositoryDep = Annotated[ExamRepositoryAdapter, Depends()]
