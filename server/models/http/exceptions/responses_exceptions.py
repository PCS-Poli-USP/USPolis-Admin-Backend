from fastapi import HTTPException, status


class UnfetchDataError(HTTPException):
    """Using uncommited or not refreshed data"""

    def __init__(self, entity: str, field: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{entity} {field} is None, try refresh the session if it is newly created",
        )
