from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.subject_type import SubjectType


class SubjectBaseDict(BaseDict, total=False):
    """
    Base class for subject dictionaries (requests and database)
    """

    name: str
    code: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int
