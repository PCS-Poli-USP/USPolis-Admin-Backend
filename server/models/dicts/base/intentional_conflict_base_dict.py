from server.models.dicts.base.base_dict import BaseDict


class IntentionalConflictBaseDict(BaseDict, total=False):
    """Base dict for intentional conflict dictionaries (requests and database).\n
    An intentional conflict has no business fields of its own - it's purely a
    pairing of two occurrences, so this dict is intentionally empty."""
