from fastapi import HTTPException, status


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
