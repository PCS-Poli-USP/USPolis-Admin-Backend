"""Shared, DB-free helper for building InstitutionalEvent objects in pure unit
tests (no session, nothing persisted): InstitutionalEventModelFactory.build()
on an unbound Session(), with an id. DB-backed tests use the factory's
create()/create_and_refresh() directly. See docs/TESTS.md's "Test data
protocol" section before adding a new make_* helper here."""

from datetime import datetime

from sqlmodel import Session

from server.models.database.institutional_event_db_model import InstitutionalEvent
from tests.factories.model.institutional_event_model_factory import (
    InstitutionalEventModelFactory,
)

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
    event = InstitutionalEventModelFactory(session=Session()).build(
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
    event.id = next(_next_id)
    return event
