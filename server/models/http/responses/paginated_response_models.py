from pydantic import BaseModel, Field
from typing import Generic, TypeVar

from server.models.page_models import MAX_PAGE_SIZE


E = TypeVar("E")
T = TypeVar("T", bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[T]):
    page: int = Field(ge=1, description="The page number")
    page_size: int = Field(
        ge=1, le=MAX_PAGE_SIZE, description="The number of items per page"
    )
    total_items: int = Field(ge=0, description="The total number of items")
    total_pages: int = Field(ge=0, description="The total number of pages")

    data: list[T] = Field(description="The list of items response")
