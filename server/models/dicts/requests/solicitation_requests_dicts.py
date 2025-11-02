from server.models.dicts.base.solicitation_base_dict import SolicitationBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.http.requests.solicitation_request_models import SolicitationData


class SolicitationRegisterDict(SolicitationBaseDict, BaseRequestDict, total=False):
    reservation_data: SolicitationData


class SolicitationApproveDict(BaseRequestDict, total=False):
    classroom_id: int
    classroom_name: str

 
class SolicitationUpdatedDict(SolicitationApproveDict):
    pass


class SolicitationDeletedDict(SolicitationRegisterDict):
    pass


class SolicitationDenyDict(BaseRequestDict):
    justification: str
