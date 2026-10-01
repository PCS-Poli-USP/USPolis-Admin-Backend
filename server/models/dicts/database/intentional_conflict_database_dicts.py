from server.models.database.occurrence_db_model import Occurrence
from server.models.dicts.base.intentional_conflict_base_dict import (
    IntentionalConflictBaseDict,
)
from server.models.dicts.database.base_database_dicts import BaseModelDict


class IntentionalConflictModelDict(
    IntentionalConflictBaseDict, BaseModelDict, total=False
):
    """TypedDict for IntentionalConflict database model."""

    first_occurrence_id: int
    second_occurrence_id: int

    first_occurrence: Occurrence
    second_occurrence: Occurrence
