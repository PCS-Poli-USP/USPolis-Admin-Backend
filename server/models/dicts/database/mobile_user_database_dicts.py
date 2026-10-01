from server.models.dicts.base.mobile_user_base_dict import MobileUserBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class MobileUserModelDict(BaseModelDict, MobileUserBaseDict, total=False):
    """Class to hold the model dictionary for the database."""
