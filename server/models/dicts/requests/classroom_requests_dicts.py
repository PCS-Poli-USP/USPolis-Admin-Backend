from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class ClassroomRegisterDict(BaseRequestDict, total=False):
    """TypedDict for Classroom request model.\n
    This TypedDict is used to define the structure of the Classroom data.\n
    """

    building_id: int
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    projector: bool
    air_conditioning: bool


class ClassroomUpdateDict(ClassroomRegisterDict, total=False):
    pass
