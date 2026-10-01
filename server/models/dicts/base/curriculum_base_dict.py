from server.models.dicts.base.base_dict import BaseDict


class CurriculumBaseDict(BaseDict, total=False):
    """Base dict for curriculum dictionaries (requests and database)"""

    codcur: int
    codhab: int
    AAC: int
    AEX: int
    description: str
