from typing import Annotated

from fastapi import Depends
from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.database.meeting_db_model import Meeting
from server.models.database.user_db_model import User
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.meeting_repository import MeetingRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.reservation_permission_checker import (
    ReservationPermissionChecker,
)


class MeetingRepositoryAdapter:
    def __init__(self, user: UserDep, session: SessionDep):
        self.session = session
        self.user = user
        self.checker = ReservationPermissionChecker(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(user=user, session=session)

    def get_by_id(self, id: int) -> Meeting:
        meeting = MeetingRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(meeting.reservation)
        return meeting

    def create(self, creator: User, input: MeetingRegister) -> Meeting:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.classroom_checker.check_permission(classroom)
        meeting = MeetingRepository.create(
            creator=creator, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(meeting)
        return meeting

    def update(self, id: int, input: MeetingUpdate) -> Meeting:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.classroom_checker.check_permission(classroom)
        meeting = MeetingRepository.update(
            user=self.user, id=id, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(meeting)
        return meeting


MeetingRepositoryDep = Annotated[MeetingRepositoryAdapter, Depends()]
