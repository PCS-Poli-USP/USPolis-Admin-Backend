from typing import Annotated

from fastapi import Depends
from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.database.event_db_model import Event
from server.models.database.user_db_model import User
from server.models.http.requests.event_request_models import EventRegister, EventUpdate
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.event_repository import EventRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.reservation_permission_checker import (
    ReservationPermissionChecker,
)


class EventRepositoryAdapter:
    def __init__(self, user: UserDep, session: SessionDep):
        self.session = session
        self.user = user
        self.checker = ReservationPermissionChecker(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(user=user, session=session)

    def get_by_id(self, id: int) -> Event:
        event = EventRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(event.reservation)
        return event

    def create(self, creator: User, input: EventRegister) -> Event:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.classroom_checker.check_permission(classroom)
        event = EventRepository.create(
            creator=creator, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(event)
        return event

    def update(self, id: int, input: EventUpdate) -> Event:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=self.session
        )
        self.classroom_checker.check_permission(classroom)
        event = EventRepository.update(
            user=self.user, id=id, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(event)
        return event


EventRepositoryDep = Annotated[EventRepositoryAdapter, Depends()]
