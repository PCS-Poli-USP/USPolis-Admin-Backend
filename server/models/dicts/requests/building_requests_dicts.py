from server.models.dicts.base.building_base_dict import BuildingBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class BuildingRegisterDict(BuildingBaseDict, BaseRequestDict, total=False):
    pass


class BuildingUpdateDict(BuildingRegisterDict, total=False):
    pass
