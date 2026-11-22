from datetime import datetime

from server.models.dicts.base.institutional_event_base_dict import (
    InstitutionalEventBaseDict,
)
from server.models.dicts.database.base_database_dicts import BaseModelDict


class InstitutionalEventModelDict(
    InstitutionalEventBaseDict, BaseModelDict, total=False
):
    """TypedDict for InstitutionalEvent database model.\n
    This TypedDict is used to define the structure of the InstitutionalEvent data.\n
    """

    likes: int
    created_at: datetime
    created_by_id: int | None
