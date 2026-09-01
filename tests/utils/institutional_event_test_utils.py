"""Shared, DB-free helper for building InstitutionalEvent object graphs in
pure unit tests (no session, nothing persisted).

Constructed directly rather than via a ModelFactory - InstitutionalEvent has
no relationships or foreign keys and no factory/dict scaffolding exists for
it yet, so a full base-dict/model-dict/base-factory/model-factory stack
would be pure overhead for the handful of response-model tests that need
one. See TESTS.md's "Test data protocol" section before adding a new make_*
helper here."""

from datetime import datetime

from server.models.database.institutional_event_db_model import InstitutionalEvent

_next_id = iter(range(1, 1_000_000))


def make_institutional_event(
    *,
    title: str = "Semana da Computação",
    description: str = "Evento anual do IME",
    category: str = "Palestra",
    start: datetime = datetime(2025, 9, 1, 10, 0),
    end: datetime = datetime(2025, 9, 1, 12, 0),
    location: str | None = None,
    building: str | None = None,
    classroom: str | None = None,
    external_link: str | None = None,
    likes: int = 0,
) -> InstitutionalEvent:
    event = InstitutionalEvent(
        id=next(_next_id),
        title=title,
        description=description,
        category=category,
        start=start,
        end=end,
        location=location,
        building=building,
        classroom=classroom,
        external_link=external_link,
        likes=likes,
    )
    return event
