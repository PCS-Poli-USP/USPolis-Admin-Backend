from typing import Generic, TypeVar

from sqlmodel import SQLModel, Session

from server.models.database.user_db_model import User

M = TypeVar("M", bound=SQLModel)


class PermissionChecker(Generic[M]):
    """
    Base class for permission checkers.
    """

    def __init__(self, user: User, session: Session) -> None:
        self.user = user
        self.session = session

    def check_permission(self, object: M | list[M] | int | list[int]) -> None:
        """
        Check if the user has the specified permission.
        - Parameters:
            - object (M | list[M] | int | list[int]): The object or list of objects to check permissions for.
        """
        raise NotImplementedError("Subclasses must implement this method.")
