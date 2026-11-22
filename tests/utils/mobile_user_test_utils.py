"""Shared, DB-backed helper for creating MobileUser rows in tests - keep
every such helper here instead of redeclaring local make_mobile_user
functions per test file.

This one persists (unlike academic_test_utils.py/time_test_utils.py's
DB-free build() helpers) because it backs integration/route-level tests
that need a real, queryable row - so it delegates to
MobileUserModelFactory.create_and_refresh() rather than .build(). See
docs/TESTS.md's "Test data protocol" section for when to use which."""

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

from sqlmodel import Session

from server.models.database.mobile_user_db_model import MobileUser
from tests.factories.model.mobile_user_model_factory import MobileUserModelFactory


def make_mobile_user(
    *,
    sub: str,
    session: Session,
    email: str | None = None,
    given_name: str | None = None,
    family_name: str | None = None,
    picture_url: str | None = "https://example.com/pic.png",
) -> MobileUser:
    overrides = {
        "sub": sub,
        "picture_url": picture_url,
        **({"email": email} if email is not None else {}),
        **({"given_name": given_name} if given_name is not None else {}),
        **({"family_name": family_name} if family_name is not None else {}),
    }
    return MobileUserModelFactory(session).create_and_refresh(**overrides)  # type: ignore[arg-type]


# The app sends its Google ID token raw in Authorization (no "Bearer ": a
# Bearer token would go to the web login first, see public_authenticate).
APP_TOKEN_HEADER = {"authorization": "app-token"}


@contextmanager
def signed_in_as(user: MobileUser) -> Iterator[None]:
    """Requests in this block carry a valid app token of `user` (send
    APP_TOKEN_HEADER): the token check returns the user's Google `sub`."""
    with patch(
        "server.deps.google_auth_dep.authenticate_with_google",
        return_value={"sub": user.sub},
    ):
        yield
