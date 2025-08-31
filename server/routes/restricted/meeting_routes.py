from fastapi import APIRouter, status
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("")
def create_meeting() -> JSONResponse:
    return JSONResponse(
        content={"message": "Meeting created successfully"},
        status_code=status.HTTP_201_CREATED,
    )
