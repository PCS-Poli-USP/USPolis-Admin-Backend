from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound
from google.auth.exceptions import GoogleAuthError


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


async def handle_google_auth_error(request, exc: GoogleAuthError) -> JSONResponse:  # type: ignore [no-untyped-def]
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": "Google Authentication error", "detail": str(exc)},
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(IntegrityError, handle_integrity_error)  # type: ignore [arg-type]
    app.add_exception_handler(NoResultFound, handle_no_result_found)  # type: ignore [arg-type]
    app.add_exception_handler(GoogleAuthError, handle_google_auth_error)  # type: ignore [arg-type]
