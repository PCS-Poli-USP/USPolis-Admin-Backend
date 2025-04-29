from server.models.dicts.base.classroom_base_dict import ClassroomBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class ClassroomRegisterDict(ClassroomBaseDict, BaseRequestDict, total=False):
    """TypedDict for Classroom request model.\n
    This TypedDict is used to define the structure of the Classroom data.\n
    """

    building_id: int


class ClassroomUpdateDict(ClassroomRegisterDict, total=False):
    pass
