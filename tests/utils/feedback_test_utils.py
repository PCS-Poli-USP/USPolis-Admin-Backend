"""Shared, DB-free helper for building Feedback object graphs in pure unit
tests (no session, nothing persisted).

Constructed directly rather than via a ModelFactory - no factory/dict
scaffolding exists for Feedback yet, and it's only needed by a couple of
response/request-model tests, so a full base-dict/model-dict/base-factory/
model-factory stack would be pure overhead. See TESTS.md's "Test data
protocol" section before adding a new make_* helper here."""

from datetime import datetime

from server.models.database.feedback_db_model import Feedback
from server.models.database.user_db_model import User

_next_id = iter(range(1, 1_000_000))


def make_feedback(
    *,
    user: User,
    title: str = "Sugestão",
    message: str = "Poderia adicionar filtro por prédio",
) -> Feedback:
    feedback = Feedback(
        id=next(_next_id),
        user_id=user.id,
        title=title,
        message=message,
        created_at=datetime(2025, 1, 1),
    )
    feedback.user = user
    return feedback
