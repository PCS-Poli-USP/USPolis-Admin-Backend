from typing import TypeVar, TypeGuard as TypeGuardProtocol

from fastapi import HTTPException, status

T = TypeVar("T")


class TypeGuard:
    @staticmethod
    def must_be_int(id: int | None) -> int:
        """
        TypeGuard for entities IDs that can be int | None.
        """
        if id is None:
            raise IdIsNoneException()
        return id

    @staticmethod
    def must_be_str(string: str | None) -> str:
        """
        TypeGuard for entities strings that can be str | None.
        """
        if string is None:
            raise StringIsNoneException()
        return string

    @staticmethod
    def is_not_none(value: T | None) -> TypeGuardProtocol[T]:
        """
        TypeGuard for any value that can be T | None.
        """
        return value is not None

    @staticmethod
    def ensure_not_none(value: T | None) -> T:
        """Ensure a value is not None and return it."""
        if value is None:
            raise ValueError("Value is None.")
        return value


class IdIsNoneException(HTTPException):
    def __init__(
        self,
    ) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, "ID is None.")


class StringIsNoneException(HTTPException):
    def __init__(
        self,
    ) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, "String is None.")
