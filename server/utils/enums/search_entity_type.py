from enum import Enum


class SearchEntityType(str, Enum):
    """Entity types indexed by the search_document materialized view."""

    SUBJECT = "subject"
    CLASS = "class"
    CLASSROOM = "classroom"
    BUILDING = "building"
    PROFESSOR = "professor"
    # Reservations, typed by their child row (one document per reservation).
    EXAM = "exam"
    EVENT = "event"
    # Only meetings whose title mentions "monitoria" are indexed.
    MEETING = "meeting"

    @staticmethod
    def values() -> list["SearchEntityType"]:
        return list(SearchEntityType)
