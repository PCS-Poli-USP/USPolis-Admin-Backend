from typing import Annotated
from fastapi import Depends, Query

from server.models.page_models import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, PaginationInput


def pagination_params(
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Requested number of items per page",
    ),
) -> PaginationInput:
    return PaginationInput(page=page, page_size=page_size)


PaginationDep = Annotated[PaginationInput, Depends(pagination_params)]
