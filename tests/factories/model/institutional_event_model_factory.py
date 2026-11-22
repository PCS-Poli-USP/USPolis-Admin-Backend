from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.database.user_db_model import User
from server.models.dicts.database.institutional_event_database_dicts import (
    InstitutionalEventModelDict,
)
from tests.factories.base.institutional_event_base_factory import (
    InstitutionalEventBaseFactory,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class InstitutionalEventModelFactory(BaseModelFactory[InstitutionalEvent]):
    """`creator` is who may edit or delete the event (with admins); None is an
    event with no recorded creator (created before it was recorded)."""

    def __init__(self, session: Session, creator: User | None = None) -> None:
        super().__init__(session)
        self.creator = creator
        self.core_factory = InstitutionalEventBaseFactory()

    def _get_model_type(self) -> type[InstitutionalEvent]:
        return InstitutionalEvent

    def get_defaults(self) -> InstitutionalEventModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "likes": 0,
            "created_at": datetime.now(),
            "created_by_id": self.creator.id if self.creator else None,
        }

    def create(  # type: ignore
        self, **overrides: Unpack[InstitutionalEventModelDict]
    ) -> InstitutionalEvent:
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[InstitutionalEventModelDict]
    ) -> InstitutionalEvent:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self,
        institutional_event_id: int,
        **overrides: Unpack[InstitutionalEventModelDict],
    ) -> InstitutionalEvent:
        return super().update(model_id=institutional_event_id, **overrides)
