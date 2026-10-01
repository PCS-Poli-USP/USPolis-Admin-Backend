from datetime import date, timedelta

import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.repositories.intentional_conflict_repository import (
    IntentionalConflictDifferentClassroom,
    IntentionalConflictRepository,
    IntentionalConflictSameOccurrence,
    IntentionalConflictWithoutClassroom,
)
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory


class TestCreate:
    def test_creates_a_conflict_between_two_occurrences_in_the_same_classroom(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))

        conflict = IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()
        session.refresh(conflict)

        assert conflict.first_occurrence_id == first.id
        assert conflict.second_occurrence_id == second.id

    def test_raises_for_the_same_occurrence(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh()

        with pytest.raises(IntentionalConflictSameOccurrence):
            IntentionalConflictRepository.create(
                first_occurrence=occurrence, second_occurrence=occurrence, session=session
            )

    def test_raises_when_an_occurrence_has_no_classroom(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh()
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=None
        ).create_and_refresh()

        with pytest.raises(IntentionalConflictWithoutClassroom):
            IntentionalConflictRepository.create(
                first_occurrence=first, second_occurrence=second, session=session
            )

    def test_raises_when_occurrences_are_in_different_classrooms(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh()
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=other_classroom
        ).create_and_refresh()

        with pytest.raises(IntentionalConflictDifferentClassroom):
            IntentionalConflictRepository.create(
                first_occurrence=first, second_occurrence=second, session=session
            )


class TestCreateMany:
    def test_creates_one_conflict_per_second_occurrence(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        second_a = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        second_b = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))

        conflicts = IntentionalConflictRepository.create_many(
            first_occurrence=first,
            second_occurrences=[second_a, second_b],
            session=session,
        )
        session.commit()

        assert {c.second_occurrence_id for c in conflicts} == {
            second_a.id,
            second_b.id,
        }


class TestGetAll:
    def test_returns_every_conflict(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        conflict = IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all(session=session)

        assert conflict.id in [c.id for c in conflicts]


class TestGetAllOnClassrooms:
    def test_returns_conflicts_whose_first_occurrence_is_in_the_given_classroom(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        conflict = IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all_on_classrooms(
            classroom_ids=[must_be_int(classroom.id)], session=session
        )

        assert [c.id for c in conflicts] == [conflict.id]

    def test_excludes_conflicts_of_other_classrooms(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))
        IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all_on_classrooms(
            classroom_ids=[999999], session=session
        )

        assert conflicts == []


class TestGetAllOnClassroomByRange:
    def test_returns_conflicts_within_the_range(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))
        conflict = IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all_on_classroom_by_range(
            classroom_id=must_be_int(classroom.id),
            start=date(2025, 3, 1),
            end=date(2025, 3, 31),
            session=session,
        )

        assert [c.id for c in conflicts] == [conflict.id]

    def test_excludes_conflicts_outside_the_range(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))
        IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all_on_classroom_by_range(
            classroom_id=must_be_int(classroom.id),
            start=date(1999, 1, 1),
            end=date(1999, 12, 31),
            session=session,
        )

        assert conflicts == []


class TestGetAllOnClassroomFromNow:
    def test_returns_conflicts_from_today_onward(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        upcoming_date = date.today() + timedelta(days=1)
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=upcoming_date)
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=upcoming_date)
        conflict = IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all_on_classroom_from_now(
            classroom_id=must_be_int(classroom.id), session=session
        )

        assert [c.id for c in conflicts] == [conflict.id]

    def test_excludes_conflicts_in_the_past(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        first = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2000, 1, 1))
        second = OccurrenceModelFactory(
            schedule=schedule, session=session, classroom=classroom
        ).create_and_refresh(date=date(2000, 1, 1))
        IntentionalConflictRepository.create(
            first_occurrence=first, second_occurrence=second, session=session
        )
        session.commit()

        conflicts = IntentionalConflictRepository.get_all_on_classroom_from_now(
            classroom_id=must_be_int(classroom.id), session=session
        )

        assert conflicts == []
