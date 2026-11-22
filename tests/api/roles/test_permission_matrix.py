"""Permission matrix: every route that acts on an object, under every way a
permission can (or cannot) be held.

`OPERATIONS` has one line per route classified OBJECT in route_registry (the
listings are in test_listings.py). The resource and action each one requires
come from the registry, so the two never disagree. Each operation targets an
object of building A (classroom_a for classroom operations) and is run once per
variant:

| variant   | what role_user holds                                   | expected  |
|-----------|--------------------------------------------------------|-----------|
| exact     | the action on the target                               | success   |
| none      | nothing                                                | denied    |
| other     | the action on the other building (or its classroom)    | denied    |
| read_only | READ on the target (write operations only)             | denied    |
| cascade   | the action on building A (classroom operations only)   | success   |
| wildcard  | the action on everything (-1)                          | success for READ/CREATE, denied for admin-only actions |
| legacy    | a member of building A's main group, no role           | success   |

Denied is 403, or 404 where the object is fetched within what the user can see.
"""

from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from server.models.http.responses.subject_response_models import (
    SubjectCrawlResponse,
)
from server.repositories.subject_repository import SubjectRepository
from server.services.security.role_permission_evaluator import (
    GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS,
)
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.crawler_enums import CrawlerType
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.api.roles.conftest import Grants
from tests.api.roles.route_registry import ROUTE_REGISTRY, Kind, Rule
from tests.api.roles.world import World
from tests.factories.request.class_request_factory import ClassRequestFactory
from tests.factories.request.classroom_request_factory import (
    ClassroomRequestFactory,
)
from tests.factories.request.event_request_factory import EventRequestFactory
from tests.factories.request.exam_request_factory import ExamRequestFactory
from tests.factories.request.meeting_request_factory import MeetingRequestFactory
from tests.factories.request.schedule_request_factory import ScheduleRequestFactory
from tests.factories.request.subject_request_factory import SubjectRequestFactory

DENIED = (403, 404)


@pytest.fixture(autouse=True)
def no_side_effects() -> Generator[None, None, None]:
    """No email, no JupiterWeb: the crawl is a stub that succeeds."""
    crawled = SubjectCrawlResponse(codes=[], failed=[], sucess=[], errors=[])
    with (
        patch("server.services.email.email_service.EmailService.send_email"),
        patch("server.services.email.email_service.EmailService.send_bcc_email"),
        patch.object(
            SubjectRepository,
            "crawler_create_many",
            AsyncMock(return_value=crawled),
        ),
        patch.object(
            SubjectRepository,
            "crawler_update_many",
            AsyncMock(return_value=crawled),
        ),
    ):
        yield


# -- the operations


@dataclass(frozen=True)
class Request:
    url: str
    params: dict[str, Any] | None = None
    json: Any = None
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class Operation:
    method: str
    path: str
    build: Callable[[World], Request]
    ok: int = 200
    rule: Rule = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule", ROUTE_REGISTRY[(self.method, self.path)])

    @property
    def id(self) -> str:
        return f"{self.method} {self.path}"


def _classroom_body(w: World) -> dict[str, Any]:
    factory = ClassroomRequestFactory(group=w.building_a.get_main_group())
    body: dict[str, Any] = jsonable_encoder(
        factory.create_input(building_id=must_be_int(w.building_a.id), group_ids=[])
    )
    return body


def _subject_body(w: World, update: bool = False) -> dict[str, Any]:
    factory = SubjectRequestFactory(building_ids=[must_be_int(w.building_a.id)])
    body: dict[str, Any] = jsonable_encoder(
        factory.update_input() if update else factory.create_input()
    )
    return body


def _conflict_params() -> dict[str, Any]:
    return {
        "start_time": "08:00:00",
        "end_time": "10:00:00",
        "recurrence": "Custom",
        "dates": ["2026-03-02"],
    }


def _deallocate_occurrence(w: World) -> Request:
    schedule = w.allocated_class().schedules[0]
    occurrence = schedule.occurrences[0]
    return Request(
        "/allocations/events",
        json={
            "desalocate": True,
            "all_occurrences": False,
            "start_time": str(occurrence.start_time),
            "end_time": str(occurrence.end_time),
            "building": w.building_a.name,
            "classroom": w.classroom_a.name,
            "occurrence_id": occurrence.id,
            "schedule_id": schedule.id,
        },
    )


def _schedule_body(w: World) -> dict[str, Any]:
    body: dict[str, Any] = jsonable_encoder(
        ScheduleRequestFactory(class_=w.class_a).create_input()
    )
    return body


def _approve(w: World) -> Request:
    solicitation = w.solicitation()
    return Request(
        f"/solicitations/approve/{solicitation.id}",
        json={"classroom_id": w.classroom_a.id, "classroom_name": w.classroom_a.name},
    )


def _reuse_options(w: World) -> Request:
    return Request(
        "/allocations/reuse-options",
        json={
            "building_id": w.building_a.id,
            "allocation_year": 2025,
            "targets": [{"subject_id": w.subject_a.id, "class_ids": [w.class_a.id]}],
        },
    )


def _reservation_url(suffix: str = "") -> Callable[[World], Request]:
    def build(w: World) -> Request:
        _, reservation = w.meeting_reservation()
        return Request(f"/reservations/{reservation.id}{suffix}")

    return build


OPERATIONS: list[Operation] = [
    # -- buildings
    Operation(
        "GET",
        "/buildings/occupance_reports/{building_id}",
        lambda w: Request(f"/buildings/occupance_reports/{w.building_a.id}"),
    ),
    Operation(
        "GET",
        "/conflicts/building/{building_id}",
        lambda w: Request(
            f"/conflicts/building/{w.building_a.id}", params={"type": "unintentional"}
        ),
    ),
    Operation(
        "GET",
        "/users/{building_id}",
        lambda w: Request(f"/users/{w.building_a.id}"),
    ),
    # -- classrooms
    Operation(
        "POST", "/classrooms", lambda w: Request("/classrooms", json=_classroom_body(w))
    ),
    Operation(
        "GET",
        "/classrooms/{id}",
        lambda w: Request(f"/classrooms/{w.classroom_a.id}"),
    ),
    Operation(
        "PUT",
        "/classrooms/{id}",
        lambda w: Request(f"/classrooms/{w.classroom_a.id}", json=_classroom_body(w)),
    ),
    Operation(
        "DELETE",
        "/classrooms/{id}",
        lambda w: Request(f"/classrooms/{w.classroom_a.id}"),
        ok=204,
    ),
    Operation(
        "GET",
        "/classrooms/with-conflict-count/{building_id}/{schedule_id}",
        lambda w: Request(
            f"/classrooms/with-conflict-count/{w.building_a.id}/"
            f"{w.class_a.schedules[0].id}"
        ),
    ),
    Operation(
        "POST",
        "/classrooms/with-conflict-count/{building_id}",
        lambda w: Request(
            f"/classrooms/with-conflict-count/{w.building_a.id}",
            json=_conflict_params(),
        ),
    ),
    # -- subjects
    Operation(
        "GET",
        "/subjects/{subject_id}",
        lambda w: Request(f"/subjects/{w.subject_a.id}"),
    ),
    Operation(
        "POST", "/subjects", lambda w: Request("/subjects", json=_subject_body(w))
    ),
    Operation(
        "PUT",
        "/subjects/{subject_id}",
        lambda w: Request(f"/subjects/{w.subject_a.id}", json=_subject_body(w, True)),
    ),
    Operation(
        "DELETE",
        "/subjects/{subject_id}",
        lambda w: Request(f"/subjects/{w.subject_a.id}"),
        ok=204,
    ),
    Operation(
        "POST",
        "/subjects/crawl",
        lambda w: Request(
            "/subjects/crawl",
            json={
                "subject_codes": ["MAC0110"],
                "calendar_ids": [],
                "type": CrawlerType.JUPITER,
            },
            headers={"building-id": str(w.building_a.id)},
        ),
    ),
    Operation(
        "PATCH",
        "/subjects/crawl",
        lambda w: Request(
            "/subjects/crawl",
            json={"subject_codes": [w.subject_a.code], "type": CrawlerType.JUPITER},
        ),
    ),
    # -- classes
    Operation(
        "POST",
        "/classes",
        lambda w: Request(
            "/classes",
            json=jsonable_encoder(ClassRequestFactory(w.subject_a).create_input()),
        ),
    ),
    Operation(
        "GET",
        "/classes/{class_id}",
        lambda w: Request(f"/classes/{w.allocated_class().id}"),
    ),
    Operation(
        "GET",
        "/classes/{class_id}/full",
        lambda w: Request(f"/classes/{w.allocated_class().id}/full"),
    ),
    Operation(
        "PUT",
        "/classes/{class_id}",
        lambda w: Request(
            f"/classes/{w.allocated_class().id}",
            json=jsonable_encoder(ClassRequestFactory(w.subject_a).update_input()),
        ),
    ),
    Operation(
        "DELETE",
        "/classes/{class_id}",
        lambda w: Request(f"/classes/{w.allocated_class().id}"),
        ok=204,
    ),
    Operation(
        "DELETE",
        "/classes/many/",
        lambda w: Request("/classes/many/", params={"ids": [w.allocated_class().id]}),
        ok=204,
    ),
    # -- schedules and allocation
    Operation(
        "PATCH",
        "/schedules/{schedule_id}/edit-occurrences",
        lambda w: Request(
            f"/schedules/{w.allocated_class().schedules[0].id}/edit-occurrences",
            json={"dates": ["2026-03-02"]},
        ),
    ),
    Operation(
        "POST",
        "/schedules/create-for-class/{class_id}",
        lambda w: Request(
            f"/schedules/create-for-class/{w.allocated_class().id}",
            json=_schedule_body(w),
        ),
    ),
    Operation(
        "POST",
        "/schedules/create-many-for-classes",
        lambda w: Request(
            "/schedules/create-many-for-classes",
            json={
                "inputs": [{**_schedule_body(w), "class_id": w.allocated_class().id}]
            },
        ),
        ok=201,
    ),
    Operation(
        "POST",
        "/occurrences/allocate-schedule",
        lambda w: Request(
            "/occurrences/allocate-schedule",
            params={
                "schedule_id": w.class_a.schedules[0].id,
                "classroom_id": w.classroom_a.id,
            },
        ),
    ),
    Operation(
        "POST",
        "/occurrences/allocate-schedule-many",
        lambda w: Request(
            "/occurrences/allocate-schedule-many",
            json=[
                {
                    "schedule_id": w.class_a.schedules[0].id,
                    "classroom_id": w.classroom_a.id,
                }
            ],
        ),
        ok=204,
    ),
    Operation(
        "DELETE",
        "/occurrences/remove-schedule-allocation",
        lambda w: Request(
            "/occurrences/remove-schedule-allocation",
            params={"schedule_id": w.allocated_class().schedules[0].id},
        ),
    ),
    Operation("PATCH", "/allocations/events", _deallocate_occurrence),
    Operation(
        "POST",
        "/allocations/allocate-allocation-map",
        lambda w: Request(
            "/allocations/allocate-allocation-map",
            json={
                "allocation_map": [
                    {
                        "schedule_id": w.class_a.schedules[0].id,
                        "classroom_ids": [w.classroom_a.id],
                    }
                ]
            },
        ),
    ),
    Operation("POST", "/allocations/reuse-options", _reuse_options),
    Operation(
        "GET",
        "/allocations_logs/{schedule_id}",
        lambda w: Request(f"/allocations_logs/{w.allocated_class().schedules[0].id}"),
    ),
    # -- reservations
    Operation(
        "POST",
        "/reservations/meetings",
        lambda w: Request(
            "/reservations/meetings",
            json=jsonable_encoder(MeetingRequestFactory(w.classroom_a).create_input()),
        ),
        ok=201,
    ),
    Operation(
        "PUT",
        "/reservations/meetings/{id}",
        lambda w: Request(
            f"/reservations/meetings/{w.meeting_reservation()[0]}",
            json=jsonable_encoder(MeetingRequestFactory(w.classroom_a).update_input()),
        ),
    ),
    Operation(
        "POST",
        "/reservations/exams",
        lambda w: Request(
            "/reservations/exams",
            json=jsonable_encoder(
                ExamRequestFactory(w.subject_a, w.classroom_a).create_input()
            ),
        ),
        ok=201,
    ),
    Operation(
        "PUT",
        "/reservations/exams/{id}",
        lambda w: Request(
            f"/reservations/exams/{w.exam_reservation()[0]}",
            json=jsonable_encoder(
                ExamRequestFactory(w.subject_a, w.classroom_a).update_input()
            ),
        ),
    ),
    Operation(
        "POST",
        "/reservations/events",
        lambda w: Request(
            "/reservations/events",
            json=jsonable_encoder(EventRequestFactory(w.classroom_a).create_input()),
        ),
        ok=201,
    ),
    Operation(
        "PUT",
        "/reservations/events/{id}",
        lambda w: Request(
            f"/reservations/events/{w.event_reservation()[0]}",
            json=jsonable_encoder(EventRequestFactory(w.classroom_a).update_input()),
        ),
    ),
    Operation("GET", "/reservations/{reservation_id}", _reservation_url()),
    Operation("GET", "/reservations/{reservation_id}/full", _reservation_url("/full")),
    Operation(
        "PATCH",
        "/reservations/{reservation_id}/edit-occurrences",
        lambda w: Request(
            f"/reservations/{w.meeting_reservation()[1].id}/edit-occurrences",
            json={"dates": ["2026-03-02"]},
        ),
    ),
    Operation("DELETE", "/reservations/{reservation_id}", _reservation_url()),
    # -- solicitations
    Operation(
        "POST",
        "/solicitations",
        lambda w: Request(
            "/solicitations",
            json=jsonable_encoder(w.solicitation_input(w.restricted_target())),
        ),
    ),
    Operation("PUT", "/solicitations/approve/{solicitation_id}", _approve),
    Operation(
        "PUT",
        "/solicitations/deny/{solicitation_id}",
        lambda w: Request(
            f"/solicitations/deny/{w.solicitation().id}", json={"justification": "Não"}
        ),
    ),
]

# OBJECT routes that list instead of acting on one object: test_listings.py.
LISTINGS: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "/occurrences"),
        ("GET", "/users/my-buildings"),
        ("GET", "/users/my-subjects"),
        ("GET", "/users/my-classes"),
        ("GET", "/users/my-classrooms"),
        ("GET", "/users/my-reservations"),
        ("GET", "/solicitations"),
        ("GET", "/solicitations/pending"),
    }
)


# -- the variants


def _expected(op: Operation, variant: str) -> str | None:
    """ "ok", "denied", or None when the variant does not apply."""
    action = op.rule.action
    if variant in ("exact", "legacy"):
        return "ok"
    if variant in ("none", "other"):
        return "denied"
    if variant == "read_only":
        return None if action == BuildingAction.READ else "denied"
    if variant == "cascade":
        applies = op.rule.resource == Resource.CLASSROOM and action in BuildingAction
        return "ok" if applies else None
    if variant == "wildcard":
        return "denied" if action in GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS else "ok"
    raise ValueError(variant)


VARIANTS = ("exact", "none", "other", "read_only", "cascade", "wildcard", "legacy")


def _cases() -> list[Any]:
    cases = []
    for op in OPERATIONS:
        for variant in VARIANTS:
            expected = _expected(op, variant)
            if expected is not None:
                cases.append(
                    pytest.param(op, variant, expected, id=f"{op.id} [{variant}]")
                )
    return cases


def _hold(variant: str, op: Operation, w: World, grant: Grants) -> None:
    """Give role_user what `variant` says, for `op`."""
    action = op.rule.action
    assert action is not None
    on_classroom = op.rule.resource == Resource.CLASSROOM

    def on_target(actions: list[Any]) -> None:
        if on_classroom:
            grant.classroom(w.target, actions)
        else:
            grant.building(w.building_a, actions)

    if variant == "exact":
        on_target([action])
    elif variant == "other":
        if on_classroom:
            grant.classroom(w.classroom_b, [ClassroomAction(action)])
        else:
            grant.building(w.building_b, [BuildingAction(action)])
    elif variant == "read_only":
        on_target([ClassroomAction.READ if on_classroom else BuildingAction.READ])
    elif variant == "cascade":
        grant.building(w.building_a, [BuildingAction(action)])
    elif variant == "wildcard":
        if on_classroom:
            grant.classroom(None, [ClassroomAction(action)])
        else:
            grant.building(None, [BuildingAction(action)])
    elif variant == "legacy":
        grant.legacy_group(w.building_a)


# -- the tests


def test_every_object_route_is_in_the_matrix() -> None:
    object_routes = {
        key for key, rule in ROUTE_REGISTRY.items() if rule.kind == Kind.OBJECT
    }
    in_matrix = {(op.method, op.path) for op in OPERATIONS}
    missing = object_routes - in_matrix - LISTINGS
    assert not missing, f"OBJECT routes with no line in OPERATIONS: {sorted(missing)}"
    assert not (in_matrix & LISTINGS)
    assert len(in_matrix) == len(OPERATIONS), "an operation is listed twice"


@pytest.mark.parametrize(("op", "variant", "expected"), _cases())
def test_permission(
    op: Operation,
    variant: str,
    expected: str,
    world: World,
    role_client: TestClient,
    grant: Grants,
) -> None:
    request = op.build(world)
    _hold(variant, op, world, grant)

    response = role_client.request(
        op.method,
        request.url,
        params=request.params,
        json=request.json,
        headers=request.headers,
    )

    if expected == "ok":
        assert response.status_code == op.ok, response.text
    else:
        assert response.status_code in DENIED, response.text
