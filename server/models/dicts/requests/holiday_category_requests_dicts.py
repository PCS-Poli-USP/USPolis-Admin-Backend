from server.models.dicts.base.holiday_category_base_dict import HolidayCategoryBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class HolidayCategoryRegisterDict(
    HolidayCategoryBaseDict, BaseRequestDict, total=False
):
    pass


class HolidayCategoryUpdateDict(HolidayCategoryRegisterDict, total=False):
    pass
