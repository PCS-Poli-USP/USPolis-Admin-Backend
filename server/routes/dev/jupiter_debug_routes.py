from fastapi import APIRouter, HTTPException, status

from server.models.http.requests.jupiter_request_models import JupiterLoginRequest
from server.services.jupiter_crawler.authenticated_crawler import (
    AuthenticatedJupiterCrawler,
    JupiterAuthenticationError,
)
from server.services.jupiter_crawler.models import JupiterStudentSchedule

router = APIRouter(prefix="/dev/jupiter", tags=["Dev Jupiter"])


@router.post("/scrape", response_model=JupiterStudentSchedule)
async def scrape_jupiter_schedule(input: JupiterLoginRequest) -> JupiterStudentSchedule:
    try:
        return await AuthenticatedJupiterCrawler.crawl_student_schedule_static(
            n_usp=input.n_usp,
            password=input.password,
        )
    except JupiterAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while scraping JupiterWeb: {str(exc)}",
        ) from exc
