from fastapi import APIRouter, Body

from server.deps.pagination_dep import PaginationDep
from server.deps.session_dep import SessionDep
from server.models.http.responses.feedback_response_models import FeedbackResponse
from server.models.http.responses.paginated_response_models import PaginatedResponse
from server.repositories.feedback_repository import FeedbackRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


@router.get("")
def get_all_feedbacks_paginated(
    pagination: PaginationDep, session: SessionDep
) -> PaginatedResponse[FeedbackResponse]:
    paginated_result = FeedbackRepository.get_all_paginated(
        pagination=pagination, session=session
    )
    response = PaginatedResponse[FeedbackResponse](
        page=paginated_result.page,
        page_size=paginated_result.page_size,
        total_items=paginated_result.total_items,
        total_pages=paginated_result.total_pages,
        data=FeedbackResponse.from_feedback_list(paginated_result.items),
    )
    return response
