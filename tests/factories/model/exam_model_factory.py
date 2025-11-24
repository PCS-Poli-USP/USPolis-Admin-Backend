from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.exam_db_model import Exam
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.dicts.database.exam_database_dicts import ExamModelDict
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.base.exam_base_factory import ExamBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory


class ExamModelFactory(BaseModelFactory[Exam]):
    def __init__(
        self,
        creator: User,
        classroom: Classroom,
        subject: Subject,
        session: Session,
        classes: list[Class] = [],
    ) -> None:
        super().__init__(session)
        if len(classes) > 0:
            if any([c.subject_id != subject.id for c in classes]):
                raise ValueError("Classes must be from the passed subject")

        self.creator = creator
        self.classroom = classroom
        self.subject = subject
        self.classes = classes
        self.base_factory = ExamBaseFactory(must_be_int(subject.id))
        self.faker = self.base_factory.faker
        self.reservation_factory = ReservationModelFactory(
            reservation_type=ReservationType.EXAM,
            creator=creator,
            classroom=classroom,
            session=session,
        )

    def _get_model_type(self) -> type[Exam]:
        return Exam

    def get_defaults(self) -> ExamModelDict:
        base = self.base_factory.get_base_defaults()
        reservation = self.reservation_factory.create_and_refresh()
        return {
            **base,
            "reservation_id": must_be_int(reservation.id),
            "reservation": reservation,
            "subject": self.subject,
            "classes": self.classes,
        }

    def create(self, **overrides: Unpack[ExamModelDict]) -> Exam:  # type: ignore
        """Create a event instance with default values."""
        exam = super().create(**overrides)

        # Avoid a non-used and inconsistent reservation on database, we delete the
        # reservation created on get_defaults that is call on super().create
        if "reservation" in overrides:
            self.reservation_factory.delete_last_instance()

        return exam

    def create_and_refresh(self, **overrides: Unpack[ExamModelDict]) -> Exam:  # type: ignore
        """Create a event instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, event_id: int, **overrides: Unpack[ExamModelDict]
    ) -> Exam:
        """Update a event instance with default values."""
        event = super().update(event_id, **overrides)
        event.updated_at = datetime.now()
        return event

    def update_and_refresh(  # type: ignore
        self, event_id: int, **overrides: Unpack[ExamModelDict]
    ) -> Exam:
        """Update a event, commit the session and return the instance refreshed."""
        event = self.update(event_id, **overrides)
        self.session.commit()
        self.session.refresh(event)
        return event
