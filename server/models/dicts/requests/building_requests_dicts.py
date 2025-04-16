from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class BuildingRegisterDict(BaseRequestDict, total=False):
    name: str


class BuildingUpdateDict(BuildingRegisterDict, total=False):
    pass
