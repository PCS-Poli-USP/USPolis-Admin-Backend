from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class UserUpdateDict(BaseRequestDict, total=False):
    """TypedDict for UserUpdate request model.\n
    This TypedDict is used to define the structure of the UserRegister data.\n
    """

    is_admin: bool
    building_ids: list[int] | None


class UserRegisterDict(UserUpdateDict, total=False):
    """TypedDict for UserRegister request model.\n
    This TypedDict is used to define the structure of the UserRegister data.\n
    """

    name: str
    email: str
