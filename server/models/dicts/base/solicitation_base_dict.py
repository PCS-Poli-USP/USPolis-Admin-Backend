from server.models.dicts.base.base_dict import BaseDict


class SolicitationBaseDict(BaseDict, total=False):
    """Base dict for solicitation dictionaries (requests and database)"""

    capacity: int
    required_classroom: bool
    building_id: int
