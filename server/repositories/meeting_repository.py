from fastapi import HTTPException, status
from sqlmodel import Session, select

from server.models.database.meeting_db_model import Meeting
from server.models.database.user_db_model import User
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository


class MeetingRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Meeting]:
        statement = select(Meeting)
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Meeting:
        statement = select(Meeting).where(Meeting.id == id)
        meeting = session.exec(statement).first()
        if meeting is None:
            raise MeetingNotFound()
        return meeting

    @staticmethod
    def create(*, creator: User, input: MeetingRegister, session: Session) -> Meeting:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        reservation = ReservationRepository.create(
            creator=creator, input=input, classroom=classroom, session=session
        )
        meeting = Meeting(
            reservation_id=reservation.id,  # pyright: ignore[reportArgumentType]
            reservation=reservation,
            link=input.link,
        )
        session.add(meeting)
        return meeting

    @staticmethod
    def update(
        *,
        id: int,
        user: User,
        input: MeetingUpdate,
        session: Session,
    ) -> Meeting:
        meeting = MeetingRepository.get_by_id(id=id, session=session)
        meeting.link = input.link
        session.add(meeting)
        return meeting

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        meeting = MeetingRepository.get_by_id(id=id, session=session)
        session.delete(meeting)


class MeetingNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reunião não encontrada",
        )
