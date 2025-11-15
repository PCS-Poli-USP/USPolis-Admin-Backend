from typing import Generic, TypeVar
from pydantic import BaseModel, Field

from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy.sql import func

T = TypeVar("T")

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 50


class PaginationInput(BaseModel):
    page: int = Field(ge=1, description="The page number")
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Requested number of items per page",
    )


class Page(BaseModel, Generic[T]):
    page: int = Field(ge=1, description="The page number")
    page_size: int = Field(
        ge=1, le=MAX_PAGE_SIZE, description="The number of items per page"
    )
    start_index: int = Field(ge=0, description="Starting item index")
    end_index: int = Field(ge=0, description="Ending item index")
    total_items: int = Field(ge=0, description="The total number of items")
    total_pages: int = Field(ge=0, description="The total number of pages")
    items: list[T] = Field(description="The list of items")

    @staticmethod
    def paginate(
        query: SelectOfScalar[T], input: PaginationInput, session: Session
    ) -> "Page[T]":
        """Paginate the given query based on the pagination input."""

        total_items = session.scalar(select(func.count()).select_from(query.subquery()))
        assert isinstance(total_items, int), (
            "A database error occurred when getting `total_items`"
        )

        total_pages = (total_items + input.page_size - 1) // input.page_size
        total_pages = max(total_pages, 1)
        current_page = min(input.page, total_pages)

        # Calculate the offset for pagination
        offset = (current_page - 1) * input.page_size

        # Apply limit and offset to the query
        result = session.exec(query.offset(offset).limit(input.page_size))

        # Fetch the paginated items
        items = list(result.all())

        # Calculate the rest of pagination metadata
        start_index = offset + 1 if total_items > 0 else 0
        end_index = min(offset + input.page_size, total_items)

        # Return the paginated response using the Page model
        return Page[T](
            items=items,
            total_items=total_items,
            start_index=start_index,
            end_index=end_index,
            total_pages=total_pages,
            page_size=input.page_size,  # can differ from the requested page_size
            page=current_page,  # can differ from the requested page
        )
