from server.models.dicts.base.base_dict import BaseDict


class MobileUserBaseDict(BaseDict, total=False):
    """Base dict for mobile user dictionaries (requests and database)"""

    sub: str
    email: str
    given_name: str
    family_name: str
    picture_url: str | None
