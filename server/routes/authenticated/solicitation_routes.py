import asyncio

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from server.deps.pagination_dep import PaginationDep
from server.deps.repository_adapters.solicitation_repository_adapter import (
    SolicitationRepositoryDep,
)
from server.models.http.requests.solicitation_request_models import (
    SolicitationRegister,
)
from server.models.http.responses.paginated_response_models import PaginatedResponse
from server.models.http.responses.solicitation_response_models import (
    SolicitationResponse,
)
from server.services.email.email_service import EmailService

embed = Body(..., embed=True)

router = APIRouter(prefix="/solicitations", tags=["Solicitations"])


@router.get("")
def get_all_solicitations(
    solicitation_repo: SolicitationRepositoryDep,
    pagination: PaginationDep,
) -> PaginatedResponse[SolicitationResponse]:
    paginated_result = solicitation_repo.get_all(pagination)
    response = PaginatedResponse[SolicitationResponse](
        page=paginated_result.page,
        page_size=paginated_result.page_size,
        total_items=paginated_result.total_items,
        total_pages=paginated_result.total_pages,
        data=SolicitationResponse.from_solicitation_list(paginated_result.items),
    )
    return response


@router.get("/pending")
async def get_pending_solicitations(
    solicitation_repo: SolicitationRepositoryDep,
) -> list[SolicitationResponse]:
    solicitations = solicitation_repo.get_pending()
    return SolicitationResponse.from_solicitation_list(solicitations)


@router.patch("/cancel/{solicitation_id}")
async def cancel_solicitation(
    solicitation_id: int, solicitation_repo: SolicitationRepositoryDep
) -> JSONResponse:
    """Cancel a class reservation solicitation"""
    solicitation = solicitation_repo.cancel(solicitation_id)
    users = solicitation.get_administrative_users_for_email()
    asyncio.create_task(
        EmailService.send_solicitation_cancelled_email(users, solicitation)
    )
    return JSONResponse(
        status_code=200,
        content={"message": "Solicitaçao cancelada com sucesso."},
    )


@router.post("")
async def create_solicitation(
    input: SolicitationRegister,
    solicitation_repo: SolicitationRepositoryDep,
) -> SolicitationResponse:
    """Create a class reservation solicitation"""
    solicitation = solicitation_repo.create(input)
    users = solicitation.get_administrative_users_for_email()
    asyncio.create_task(
        EmailService.send_solicitation_request_email(users, solicitation)
    )
    return SolicitationResponse.from_solicitation(solicitation)


@router.put("/{solicitation_id}")
async def update_solicitation(
    solicitation_id: int,
    input: SolicitationRegister,
    solicitation_repo: SolicitationRepositoryDep,
) -> SolicitationResponse:
    solicitation = solicitation_repo.update(solicitation_id, input)
    return SolicitationResponse.from_solicitation(solicitation)
