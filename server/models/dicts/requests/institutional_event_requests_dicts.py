from server.models.dicts.base.institutional_event_base_dict import (
    InstitutionalEventBaseDict,
)
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class InstitutionalEventRegisterDict(
    InstitutionalEventBaseDict, BaseRequestDict, total=False
):
    pass


class InstitutionalEventUpdateDict(InstitutionalEventRegisterDict, total=False):
    pass
