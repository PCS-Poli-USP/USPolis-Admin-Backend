from pydantic import BaseModel, Field

from server.utils.enums.search_entity_type import SearchEntityType


class SearchLogRequest(BaseModel):
    """A search the user settled on. Only the query and the type filter are
    sent: the server recomputes the number of results itself."""

    q: str = Field(min_length=2, max_length=100)
    types: list[SearchEntityType] | None = None
