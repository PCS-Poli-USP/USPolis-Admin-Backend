from datetime import date

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.exam_repository import (
    ExamInvalidClassAndSubject,
    ExamNotFound,
    ExamRepository,
)
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.request.exam_request_factory import ExamRequestFactory
from tests.utils.validators.exam.exam_model_validator import ExamModelAsserts


class TestCreate:
    def test_creates_an_exam_with_its_classes(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()

        exam = ExamRepository.create(creator=admin_user, input=input, session=session)
        session.commit()
        session.refresh(exam)

        ExamModelAsserts.assert_exam_after_create(exam, input)

    def test_raises_when_a_class_belongs_to_a_different_subject(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        session: Session,
    ) -> None:
        other_subject = SubjectModelFactory(
            building=subject.buildings[0], session=session
        ).create_and_refresh()
        other_class = ClassModelFactory(
            subject=other_subject, session=session
        ).create_and_refresh()

        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[other_class]
        ).create_input()

        with pytest.raises(ExamInvalidClassAndSubject):
            ExamRepository.create(creator=admin_user, input=input, session=session)

    def test_allocate_false_leaves_the_reservation_pending(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()

        exam = ExamRepository.create(
            creator=admin_user, input=input, session=session, allocate=False
        )
        session.commit()
        session.refresh(exam)

        assert exam.reservation.status == ReservationStatus.PENDING


class TestGetById:
    def test_returns_the_matching_exam(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        created = ExamRepository.create(
            creator=admin_user, input=input, session=session
        )
        session.commit()

        found = ExamRepository.get_by_id(id=must_be_int(created.id), session=session)

        assert found.id == created.id

    def test_raises_when_exam_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ExamNotFound):
            ExamRepository.get_by_id(id=999999, session=session)


class TestGetAll:
    def test_returns_exams_active_today_by_default(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        exam = ExamRepository.create(creator=admin_user, input=input, session=session)
        session.commit()

        exams = ExamRepository.get_all(session=session, interval=QueryInterval())

        assert exam.id in [e.id for e in exams]

    def test_excludes_exams_outside_the_start_end_interval(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        exam = ExamRepository.create(creator=admin_user, input=input, session=session)
        session.commit()

        exams = ExamRepository.get_all(
            session=session,
            interval=QueryInterval(start=date(1999, 1, 1), end=date(1999, 12, 31)),
        )

        assert exam.id not in [e.id for e in exams]


class TestGetAllBySubjectId:
    def test_returns_exams_of_the_given_subject(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        exam = ExamRepository.create(creator=admin_user, input=input, session=session)
        session.commit()

        exams = ExamRepository.get_all_by_subject_id(
            subject_id=must_be_int(subject.id),
            session=session,
            interval=QueryInterval(),
        )

        assert exam.id in [e.id for e in exams]

    def test_returns_empty_for_a_subject_with_no_exams(
        self, subject: Subject, session: Session
    ) -> None:
        exams = ExamRepository.get_all_by_subject_id(
            subject_id=must_be_int(subject.id),
            session=session,
            interval=QueryInterval(),
        )

        assert exams == []


class TestGetAllByClassId:
    def test_returns_exams_linked_to_the_given_class(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        exam = ExamRepository.create(creator=admin_user, input=input, session=session)
        session.commit()

        exams = ExamRepository.get_all_by_class_id(
            class_id=must_be_int(class_.id), session=session, interval=QueryInterval()
        )

        assert exam.id in [e.id for e in exams]

    def test_returns_empty_for_a_class_with_no_exams(
        self, class_: Class, session: Session
    ) -> None:
        exams = ExamRepository.get_all_by_class_id(
            class_id=must_be_int(class_.id), session=session, interval=QueryInterval()
        )

        assert exams == []


class TestUpdate:
    def test_updates_the_subject_and_classes(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        create_input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        exam = ExamRepository.create(
            creator=admin_user, input=create_input, session=session
        )
        session.commit()

        other_class = ClassModelFactory(
            subject=subject, session=session
        ).create_and_refresh()
        update_input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[other_class]
        ).update_input()

        updated = ExamRepository.update(
            user=admin_user,
            id=must_be_int(exam.id),
            input=update_input,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        ExamModelAsserts.assert_exam_after_update(updated, update_input)

    def test_raises_when_a_class_belongs_to_a_different_subject(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        create_input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).create_input()
        exam = ExamRepository.create(
            creator=admin_user, input=create_input, session=session
        )
        session.commit()

        other_subject = SubjectModelFactory(
            building=subject.buildings[0], session=session
        ).create_and_refresh()
        other_class = ClassModelFactory(
            subject=other_subject, session=session
        ).create_and_refresh()
        update_input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[other_class]
        ).update_input()

        with pytest.raises(ExamInvalidClassAndSubject):
            ExamRepository.update(
                user=admin_user,
                id=must_be_int(exam.id),
                input=update_input,
                session=session,
            )

    def test_raises_when_exam_does_not_exist(
        self,
        admin_user: User,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        update_input = ExamRequestFactory(
            subject=subject, classroom=classroom, classes=[class_]
        ).update_input()

        with pytest.raises(ExamNotFound):
            ExamRepository.update(
                user=admin_user, id=999999, input=update_input, session=session
            )
