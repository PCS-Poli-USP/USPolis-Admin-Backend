from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from server.models.database.base_db_model import BaseModel
from server.models.database.occurrence_db_model import Occurrence


class IntentionalConflict(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "first_occurrence_id",
            "second_occurrence_id",
            name="unique_occurrence_pair",
        ),
    )

    first_occurrence: Occurrence = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "IntentionalConflict.first_occurrence_id"
        }
    )

    second_occurrence: Occurrence = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "IntentionalConflict.second_occurrence_id"
        }
    )

    first_occurrence_id: int = Field(foreign_key="occurrence.id", ondelete="CASCADE")
    second_occurrence_id: int = Field(foreign_key="occurrence.id", ondelete="CASCADE")
