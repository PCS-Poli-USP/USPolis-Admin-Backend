from fastapi import HTTPException, status


def must_be_int(id: int | None) -> int:
    """
    TypeGuard for entities IDs that can be int | None.
    """
    if id is None:
        raise IdIsNoneException()
    return id


class IdIsNoneException(HTTPException):
    def __init__(
        self,
    ) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, "ID is None.")
