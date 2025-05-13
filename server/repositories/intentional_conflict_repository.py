from fastapi import HTTPException, status
from sqlmodel import Session
from server.models.database.intentional_conflict_db_model import IntentionalConflict
from server.models.database.occurrence_db_model import Occurrence
from server.utils.must_be_int import must_be_int


class IntentionalConflictRepository:
    @staticmethod
    def create(
        first_occurrence: Occurrence, second_occurrence: Occurrence, session: Session
    ) -> IntentionalConflict:
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


class SameOccurrenceError(HTTPException):
    """Exception raised when trying to create an intentional conflict with the same occurrence."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível criar um conflito intencional entre a mesma ocorrência.",
        )
