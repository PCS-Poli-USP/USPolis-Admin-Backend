"""The objects the table-driven role tests act on (the `world` fixture).

The fixtures of tests/api/roles/conftest.py (two buildings, their classrooms,
subjects and classes), plus helpers that create, as an admin and through the
factories and repositories, the objects an operation acts on. Everything
defaults to building A; pass the B objects for the other side.
"""

from dataclasses import dataclass

from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.http.requests.solicitation_request_models import (
    SolicitationRegister,
)
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.solicitation_repository import SolicitationRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.event_model_factory import EventModelFactory
from tests.factories.model.exam_model_factory import ExamModelFactory
from tests.factories.model.meeting_model_factory import MeetingModelFactory
from tests.factories.request.solicitation_request_factory import (
    SolicitationRequestFactory,
)


@dataclass
class World:
    session: Session
    admin: User
    building_a: Building
    building_b: Building
    classroom_a: Classroom
    classroom_b: Classroom
    subject_a: Subject
    subject_b: Subject
    class_a: Class
    class_b: Class
    # The classroom a classroom operation acts on (and the variants grant on).
    target: Classroom

    def allocated_class(
        self, class_: Class | None = None, classroom: Classroom | None = None
    ) -> Class:
        """A class (class_a) with its schedule allocated in a classroom
        (classroom_a)."""
        class_ = class_ or self.class_a
        self._allocate(class_.schedules[0], classroom or self.classroom_a)
        self.session.refresh(class_)
        return class_

    def _allocate(self, schedule: Schedule, classroom: Classroom) -> None:
        OccurrenceRepository.allocate_schedule(
            user=self.admin,
            classroom=classroom,
            schedule=schedule,
            session=self.session,
        )
        self.session.commit()

    def _allocated(self, reservation: Reservation, classroom: Classroom) -> Reservation:
        self._allocate(reservation.schedule, classroom)
        self.session.refresh(reservation)
        return reservation

    def meeting_reservation(
        self, classroom: Classroom | None = None
    ) -> tuple[int, Reservation]:
        """A meeting allocated in a classroom (classroom_a): (meeting id,
        reservation)."""
        classroom = classroom or self.classroom_a
        meeting = MeetingModelFactory(
            classroom=classroom, creator=self.admin, session=self.session
        ).create_and_refresh()
        return must_be_int(meeting.id), self._allocated(meeting.reservation, classroom)

    def exam_reservation(self) -> tuple[int, Reservation]:
        exam = ExamModelFactory(
            creator=self.admin,
            classroom=self.classroom_a,
            subject=self.subject_a,
            session=self.session,
        ).create_and_refresh()
        return must_be_int(exam.id), self._allocated(exam.reservation, self.classroom_a)

    def event_reservation(self) -> tuple[int, Reservation]:
        event = EventModelFactory(
            classroom=self.classroom_a, creator=self.admin, session=self.session
        ).create_and_refresh()
        return must_be_int(event.id), self._allocated(
            event.reservation, self.classroom_a
        )

    def solicitation_input(
        self, classroom: Classroom, building: Building | None = None
    ) -> SolicitationRegister:
        return SolicitationRequestFactory(
            building or self.building_a, classroom
        ).create_input(required_classroom=False)

    def solicitation(
        self,
        building: Building | None = None,
        classroom: Classroom | None = None,
        requester: User | None = None,
        with_classroom: bool = True,
    ) -> Solicitation:
        """A pending solicitation for a classroom (classroom_a) of a building
        (building_a), requested by someone (the admin). `with_classroom=False`:
        for the building only, no classroom asked for."""
        input = self.solicitation_input(
            classroom or self.classroom_a, building or self.building_a
        )
        if not with_classroom:
            input.reservation_data.classroom_id = None
        solicitation = SolicitationRepository.create(
            requester=requester or self.admin, input=input, session=self.session
        )
        self.session.commit()
        self.session.refresh(solicitation)
        return solicitation

    def restricted_target(self) -> Classroom:
        """A new restricted classroom of building A, made the target: requesting
        a solicitation only takes REQUEST on a restricted classroom (anyone
        logged in requests the others)."""
        self.target = ClassroomModelFactory(
            session=self.session, creator=self.admin, building=self.building_a
        ).create_and_refresh(restricted=True)
        return self.target
