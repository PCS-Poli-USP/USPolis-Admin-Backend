"""Routes whose object belongs to someone (route_registry Kind.OWNER).

User schedules are personal: only the owner edits or deletes one, admins
included. A solicitation is edited only by who requested it, and cancelled by
them or an admin. Global entities (holiday categories, holidays, calendars,
institutional events): any restricted user creates one, and only its creator
or an admin edits or deletes it.

`OWNER_OPERATIONS` has one line per OWNER route of the registry; each runs as
the owner, as another user and as an admin. The classes below pin the rules
the table does not show (what changes, objects with no creator, ...).
"""

from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.institutional_event_db_model import InstitutionalEvent
from server.models.database.user_db_model import User
from server.models.database.user_schedule_db_model import UserSchedule
from server.utils.enums.actions_enums import ClassroomAction
from tests.api.roles.conftest import Grants
from tests.api.roles.route_registry import ROUTE_REGISTRY, Kind
from tests.api.roles.world import World
from tests.factories.model.calendar_model_factory import CalendarModelFactory
from tests.factories.model.holiday_category_model_factory import (
    HolidayCategoryModelFactory,
)
from tests.factories.model.holiday_model_factory import HolidayModelFactory
from tests.factories.model.institutional_event_model_factory import (
    InstitutionalEventModelFactory,
)
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.model.user_schedule_model_factory import (
    UserScheduleModelFactory,
)
from tests.factories.request.calendar_request_factory import CalendarRequestFactory
from tests.factories.request.holiday_category_request_factory import (
    HolidayCategoryRequestFactory,
)
from tests.factories.request.holiday_request_factory import HolidayRequestFactory
from tests.factories.request.institutional_event_request_factory import (
    InstitutionalEventRequestFactory,
)
from tests.factories.request.solicitation_request_factory import (
    SolicitationRequestFactory,
)
from tests.utils.mobile_user_test_utils import (
    APP_TOKEN_HEADER,
    make_mobile_user,
    signed_in_as,
)

SCHEDULES = "/users/schedules"
EVENTS = "/institutional_events"


def _other_user(session: Session) -> User:
    return UserModelFactory(session=session).create_and_refresh(is_admin=False)


def _user_schedule(owner: User, session: Session) -> UserSchedule:
    return UserScheduleModelFactory(user=owner, session=session).create_and_refresh()


class TestUserSchedules:
    def test_the_owner_edits_their_schedule(
        self, role_client: TestClient, role_user: User, session: Session
    ) -> None:
        schedule = _user_schedule(role_user, session)

        response = role_client.put(
            f"{SCHEDULES}/{schedule.id}", json={"schedule_ids": []}
        )

        assert response.status_code == status.HTTP_200_OK, response.text

    def test_nobody_else_edits_it(
        self, role_client: TestClient, session: Session
    ) -> None:
        owner = _other_user(session)
        schedule = _user_schedule(owner, session)
        start, end = schedule.start_date, schedule.end_date

        response = role_client.put(
            f"{SCHEDULES}/{schedule.id}", json={"schedule_ids": []}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
        session.refresh(schedule)
        assert (schedule.start_date, schedule.end_date) == (start, end)

    def test_nobody_else_deletes_it(
        self, role_client: TestClient, session: Session
    ) -> None:
        schedule = _user_schedule(_other_user(session), session)

        response = role_client.delete(f"{SCHEDULES}/{schedule.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
        assert session.get(UserSchedule, schedule.id) is not None

    def test_not_even_an_admin(self, client: TestClient, session: Session) -> None:
        schedule = _user_schedule(_other_user(session), session)

        response = client.put(f"{SCHEDULES}/{schedule.id}", json={"schedule_ids": []})

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text


def _event_body(title: str = "Semana da Computação") -> dict[str, Any]:
    body: dict[str, Any] = jsonable_encoder(
        InstitutionalEventRequestFactory().create_input(title=title)
    )
    return body


def _event(session: Session, created_by: User | None) -> InstitutionalEvent:
    return InstitutionalEventModelFactory(
        session=session, creator=created_by
    ).create_and_refresh(title="Semana da Computação")


class TestInstitutionalEvents:
    """role_user passes the restricted gate with any role."""

    def test_creating_records_the_creator(
        self,
        role_client: TestClient,
        role_user: User,
        grant: Grants,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.post(EVENTS, json=_event_body())

        assert response.status_code == status.HTTP_200_OK, response.text
        event = session.get(InstitutionalEvent, response.json()["id"])
        assert event is not None and event.created_by_id == role_user.id

    def test_the_creator_edits_and_deletes(
        self,
        role_client: TestClient,
        role_user: User,
        grant: Grants,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])
        event = _event(session, created_by=role_user)

        edited = role_client.put(f"{EVENTS}/{event.id}", json=_event_body("Nova"))
        deleted = role_client.delete(f"{EVENTS}/{event.id}")

        assert edited.status_code == status.HTTP_200_OK, edited.text
        assert edited.json()["title"] == "Nova"
        assert deleted.status_code == status.HTTP_204_NO_CONTENT, deleted.text

    def test_nobody_else_edits_or_deletes(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])
        event = _event(session, created_by=_other_user(session))

        edited = role_client.put(f"{EVENTS}/{event.id}", json=_event_body("Nova"))
        deleted = role_client.delete(f"{EVENTS}/{event.id}")

        assert edited.status_code == status.HTTP_403_FORBIDDEN, edited.text
        assert deleted.status_code == status.HTTP_403_FORBIDDEN, deleted.text
        session.refresh(event)
        assert event.title == "Semana da Computação"

    def test_an_event_with_no_creator_is_admin_only(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])
        event = _event(session, created_by=None)

        response = role_client.put(f"{EVENTS}/{event.id}", json=_event_body("Nova"))

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text

    def test_an_admin_edits_and_deletes_any(
        self, client: TestClient, session: Session
    ) -> None:
        event = _event(session, created_by=_other_user(session))
        orphan = _event(session, created_by=None)

        edited = client.put(f"{EVENTS}/{event.id}", json=_event_body("Nova"))
        deleted = client.delete(f"{EVENTS}/{orphan.id}")

        assert edited.status_code == status.HTTP_200_OK, edited.text
        assert deleted.status_code == status.HTTP_204_NO_CONTENT, deleted.text

    def test_a_like_from_the_app_is_not_an_edit(
        self, public_client: TestClient, session: Session
    ) -> None:
        event = _event(session, created_by=_other_user(session))
        app_user = make_mobile_user(sub="app-user", session=session)

        with signed_in_as(app_user):
            response = public_client.patch(
                "/mobile/institutional-events",
                json={"event_id": event.id, "user_id": app_user.id, "like": True},
                headers=APP_TOKEN_HEADER,
            )

        assert response.status_code == status.HTTP_200_OK, response.text
        session.refresh(event)
        assert event.likes == 1


# -- the table: owner, someone else, admin


@dataclass(frozen=True)
class OwnerOperation:
    method: str
    path: str
    # Creates the object, owned by the given user, and returns (url, body).
    build: Callable[[World, User], tuple[str, Any]]
    ok: int = 200
    admin_allowed: bool = True

    @property
    def id(self) -> str:
        return f"{self.method} {self.path}"


def _body(model: Any) -> Any:
    return jsonable_encoder(model)


def _schedule(w: World, owner: User) -> str:
    return f"{SCHEDULES}/{_user_schedule(owner, w.session).id}"


def _category(w: World, owner: User) -> Any:
    return HolidayCategoryModelFactory(
        creator=owner, session=w.session
    ).create_and_refresh()


def _holiday(w: World, owner: User) -> tuple[str, Any]:
    category = _category(w, w.admin)
    holiday = HolidayModelFactory(
        creator=owner, category=category, session=w.session
    ).create_and_refresh()
    return f"/holidays/{holiday.id}", _body(
        HolidayRequestFactory(category).update_input()
    )


def _calendar(w: World, owner: User) -> str:
    calendar = CalendarModelFactory(
        creator=owner, session=w.session
    ).create_and_refresh()
    return f"/calendars/{calendar.id}"


def _event_of(w: World, owner: User) -> str:
    event = InstitutionalEventModelFactory(
        session=w.session, creator=owner
    ).create_and_refresh()
    return f"{EVENTS}/{event.id}"


def _solicitation(w: World, owner: User) -> str:
    return str(w.solicitation(requester=owner).id)


OWNER_OPERATIONS: list[OwnerOperation] = [
    OwnerOperation(
        "PUT",
        "/users/schedules/{user_schedule_id}",
        lambda w, u: (_schedule(w, u), {"schedule_ids": []}),
        admin_allowed=False,
    ),
    OwnerOperation(
        "DELETE",
        "/users/schedules/{user_schedule_id}",
        lambda w, u: (_schedule(w, u), None),
        admin_allowed=False,
    ),
    OwnerOperation(
        "PUT",
        "/holidays_categories/{holiday_category_id}",
        lambda w, u: (
            f"/holidays_categories/{_category(w, u).id}",
            _body(HolidayCategoryRequestFactory().update_input()),
        ),
    ),
    OwnerOperation(
        "DELETE",
        "/holidays_categories/{holiday_category_id}",
        lambda w, u: (f"/holidays_categories/{_category(w, u).id}", None),
        ok=204,
    ),
    OwnerOperation("PUT", "/holidays/{holiday_id}", _holiday),
    OwnerOperation(
        "DELETE",
        "/holidays/{holiday_id}",
        lambda w, u: (_holiday(w, u)[0], None),
        ok=204,
    ),
    OwnerOperation(
        "PUT",
        "/calendars/{calendar_id}",
        lambda w, u: (
            _calendar(w, u),
            _body(CalendarRequestFactory().update_input()),
        ),
    ),
    OwnerOperation(
        "DELETE",
        "/calendars/{calendar_id}",
        lambda w, u: (_calendar(w, u), None),
        ok=204,
    ),
    OwnerOperation(
        "PUT",
        "/institutional_events/{institutional_event_id}",
        lambda w, u: (
            _event_of(w, u),
            _body(InstitutionalEventRequestFactory().update_input()),
        ),
    ),
    OwnerOperation(
        "DELETE",
        "/institutional_events/{institutional_event_id}",
        lambda w, u: (_event_of(w, u), None),
        ok=204,
    ),
    OwnerOperation(
        "PUT",
        "/solicitations/{solicitation_id}",
        lambda w, u: (
            f"/solicitations/{_solicitation(w, u)}",
            _body(
                SolicitationRequestFactory(w.building_a, w.classroom_a).create_input(
                    required_classroom=False
                )
            ),
        ),
        admin_allowed=False,
    ),
    OwnerOperation(
        "PATCH",
        "/solicitations/cancel/{solicitation_id}",
        lambda w, u: (f"/solicitations/cancel/{_solicitation(w, u)}", None),
    ),
]


def _owner_cases() -> list[Any]:
    return [
        pytest.param(op, who, id=f"{op.id} [{who}]")
        for op in OWNER_OPERATIONS
        for who in ("owner", "other", "admin")
    ]


def test_every_owner_route_is_in_the_table() -> None:
    owner_routes = {
        key for key, rule in ROUTE_REGISTRY.items() if rule.kind == Kind.OWNER
    }
    assert {(op.method, op.path) for op in OWNER_OPERATIONS} == owner_routes


@pytest.fixture
def no_emails() -> Generator[None, None, None]:
    """Cancelling a solicitation notifies by email."""
    with (
        patch("server.services.email.email_service.EmailService.send_email"),
        patch("server.services.email.email_service.EmailService.send_bcc_email"),
    ):
        yield


@pytest.mark.parametrize(("op", "who"), _owner_cases())
def test_owner_route(
    op: OwnerOperation,
    who: str,
    world: World,
    role_user: User,
    request: pytest.FixtureRequest,
    no_emails: None,
) -> None:
    owner = role_user if who == "owner" else _other_user(world.session)
    url, body = op.build(world, owner)
    if who == "admin":
        client: TestClient = request.getfixturevalue("client")
    else:
        # Any role passes the restricted gate; it grants nothing on the object.
        grants: Grants = request.getfixturevalue("grant")
        grants.classroom(world.classroom_b, [ClassroomAction.READ])
        client = request.getfixturevalue("role_client")

    response = client.request(op.method, url, json=body)

    allowed = who == "owner" or (who == "admin" and op.admin_allowed)
    if allowed:
        assert response.status_code == op.ok, response.text
    else:
        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
