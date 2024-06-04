class UnfetchDataError(ValueError):
    """Using uncommited or not refreshed data"""

    def __init__(self, entity: str, field: str) -> None:
        super().__init__(
            f"{entity} {field} is None, try refresh the session if it is newly created"
        )
