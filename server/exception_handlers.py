from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound


async def handle_integrity_error(request, exc: IntegrityError) -> JSONResponse:  # type: ignore [no-untyped-def]
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": "Integrity error", "detail": str(exc.orig)},
    )


async def handle_no_result_found(request, exc: NoResultFound) -> JSONResponse:  # type: ignore [no-untyped-def]
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "No result found", "detail": str(exc._message())},
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IntegrityError, handle_integrity_error)  # type: ignore [arg-type]
    app.add_exception_handler(NoResultFound, handle_no_result_found)  # type: ignore [arg-type]
