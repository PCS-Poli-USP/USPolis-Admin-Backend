from enum import StrEnum


class APISecurityLevel(StrEnum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    RESTRICTED = "restricted"
    ADMIN = "admin"
    UNKNOWN = "unknown"

    @classmethod
    def get_from_tags(cls, tags: list[str]) -> "APISecurityLevel":
        if "Admin" in tags:
            return cls.ADMIN
        if "Restricted" in tags:
            return cls.RESTRICTED
        if "Authenticated" in tags:
            return cls.AUTHENTICATED
        if "Public" in tags:
            return cls.PUBLIC
        return cls.UNKNOWN
