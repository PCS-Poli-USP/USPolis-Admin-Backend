from server.models.dicts.base.base_dict import BaseDict


class ApiClientBaseDict(BaseDict, total=False):
    """Base dict for API client dictionaries (requests and database)"""

    name: str
    organization: str | None
    contact_name: str
    contact_email: str
    description: str
