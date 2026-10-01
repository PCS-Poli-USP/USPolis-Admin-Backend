from typing import Unpack

from sqlmodel import Session

from server.models.database.intentional_conflict_db_model import IntentionalConflict
from server.models.database.occurrence_db_model import Occurrence
from server.models.dicts.database.intentional_conflict_database_dicts import (
    IntentionalConflictModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.intentional_conflict_base_factory import (
    IntentionalConflictBaseFactory,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class IntentionalConflictModelFactory(BaseModelFactory[IntentionalConflict]):
    def __init__(
        self, first_occurrence: Occurrence, second_occurrence: Occurrence, session: Session
    ) -> None:
        super().__init__(session)
        self.first_occurrence = first_occurrence
        self.second_occurrence = second_occurrence
        self.core_factory = IntentionalConflictBaseFactory()

    def _get_model_type(self) -> type[IntentionalConflict]:
        return IntentionalConflict

    def get_defaults(self) -> IntentionalConflictModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "first_occurrence_id": must_be_int(self.first_occurrence.id),
            "second_occurrence_id": must_be_int(self.second_occurrence.id),
            "first_occurrence": self.first_occurrence,
            "second_occurrence": self.second_occurrence,
        }

    def create(  # type: ignore
        self, **overrides: Unpack[IntentionalConflictModelDict]
    ) -> IntentionalConflict:
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[IntentionalConflictModelDict]
    ) -> IntentionalConflict:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, intentional_conflict_id: int, **overrides: Unpack[IntentionalConflictModelDict]
    ) -> IntentionalConflict:
        return super().update(model_id=intentional_conflict_id, **overrides)
