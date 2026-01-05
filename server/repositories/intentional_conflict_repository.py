from datetime import date
from fastapi import HTTPException, status
from sqlmodel import Session, col, select
from sqlalchemy.orm import aliased
from server.models.database.intentional_conflict_db_model import IntentionalConflict
from server.models.database.occurrence_db_model import Occurrence
from server.utils.must_be_int import must_be_int


class IntentionalConflictRepository:
    @staticmethod
    def create(
        first_occurrence: Occurrence, second_occurrence: Occurrence, session: Session
    ) -> IntentionalConflict:
        if first_occurrence.id == second_occurrence.id:
            raise IntentionalConflictSameOccurrence()

        if not first_occurrence.classroom or not second_occurrence.classroom:
            raise IntentionalConflictWithoutClassroom()

        if first_occurrence.classroom_id != second_occurrence.classroom_id:
            raise IntentionalConflictDifferentClassroom()

        intentional_conflict = IntentionalConflict(
            first_occurrence_id=must_be_int(first_occurrence.id),
            second_occurrence_id=must_be_int(second_occurrence.id),
        )
        session.add(intentional_conflict)
        return intentional_conflict

    @staticmethod
    def create_many(
        first_occurrence: Occurrence,
        second_occurrences: list[Occurrence],
        session: Session,
    ) -> list[IntentionalConflict]:
        conflicts = [
            IntentionalConflictRepository.create(
                first_occurrence=first_occurrence,
                second_occurrence=second_occurrence,
                session=session,
            )
            for second_occurrence in second_occurrences
        ]
        return conflicts

    @staticmethod
    def get_all(
        session: Session,
    ) -> list[IntentionalConflict]:
        statement = select(IntentionalConflict)
        conflicts = session.exec(statement).all()
        return list(conflicts)

    @staticmethod
    def get_all_on_classrooms(
        classroom_ids: list[int],
        session: Session,
    ) -> list[IntentionalConflict]:
        statement = (
            select(IntentionalConflict)
            .join(
                Occurrence,
                col(IntentionalConflict.first_occurrence_id) == col(Occurrence.id),
            )
            .where(col(Occurrence.classroom_id).in_(classroom_ids))
        )
        conflicts = session.exec(statement).all()
        return list(conflicts)

    @staticmethod
    def get_all_on_classroom_by_range(
        classroom_id: int,
        start: date,
        end: date,
        session: Session,
    ) -> list[IntentionalConflict]:
        Occurrence1 = aliased(Occurrence)
        Occurrence2 = aliased(Occurrence)

        statement = (
            select(IntentionalConflict)
            .join(
                Occurrence1,
                col(IntentionalConflict.first_occurrence_id) == Occurrence1.id,
            )
            .join(
                Occurrence2,
                col(IntentionalConflict.second_occurrence_id) == Occurrence2.id,
            )
            .where(
                Occurrence1.classroom_id == Occurrence2.classroom_id,
                Occurrence1.classroom_id == classroom_id,
                Occurrence1.date == Occurrence2.date,
                Occurrence1.date >= start,
                Occurrence1.date <= end,
            )
        )
        conflicts = session.exec(statement).all()
        return list(conflicts)

    @staticmethod
    def get_all_on_classroom_from_now(
        classroom_id: int,
        session: Session,
    ) -> list[IntentionalConflict]:
        Occurrence1 = aliased(Occurrence)
        Occurrence2 = aliased(Occurrence)
        today = date.today()
        statement = (
            select(IntentionalConflict)
            .join(
                Occurrence1,
                col(IntentionalConflict.first_occurrence_id) == Occurrence1.id,
            )
            .join(
                Occurrence2,
                col(IntentionalConflict.second_occurrence_id) == Occurrence2.id,
            )
            .where(
                Occurrence1.classroom_id == Occurrence2.classroom_id,
                Occurrence1.classroom_id == classroom_id,
                Occurrence1.date == Occurrence2.date,
                Occurrence1.date >= today,
            )
        )
        conflicts = session.exec(statement).all()
        return list(conflicts)


class IntentionalConflictSameOccurrence(HTTPException):
    """Exception raised when trying to create an intentional conflict with the same occurrence."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível criar um conflito intencional entre si mesmo.",
        )


class IntentionalConflictWithoutClassroom(HTTPException):
    """Exception raised when trying to create an intentional conflict with one or both occurrences without a classroom."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O conflito intentional deve ter uma sala.",
        )


class IntentionalConflictDifferentClassroom(HTTPException):
    """Exception raised when trying to create an intentional conflict with occurrences in different classrooms."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O conflito intencional deve ser entre ocorrências na mesma sala.",
        )
