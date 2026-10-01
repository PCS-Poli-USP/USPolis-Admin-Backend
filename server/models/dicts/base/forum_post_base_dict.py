from server.models.dicts.base.base_dict import BaseDict


class ForumPostBaseDict(BaseDict, total=False):
    """Base dict for forum post dictionaries (requests and database)"""

    content: str | None
