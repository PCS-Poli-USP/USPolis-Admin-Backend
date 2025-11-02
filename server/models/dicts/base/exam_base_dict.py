from server.models.dicts.base.base_dict import BaseDict


class ExamBaseDict(BaseDict, total=False):
    """Base dict for exam dictionaries (requests and database)"""

    subject_id: int
