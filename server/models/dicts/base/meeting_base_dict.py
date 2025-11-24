from server.models.dicts.base.base_dict import BaseDict


class MeetingBaseDict(BaseDict, total=False):
    """Base dict for meeting dictionaries (requests and database)"""

    link: str | None
