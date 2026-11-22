"""Implied actions through the API (role_permission_evaluator.IMPLIED_ACTIONS).

`IMPLICATIONS` has one line per (granted, implied) pair of IMPLIED_ACTIONS: a
role holding only `granted` on the target does a request that takes `implied`.
`NOT_IMPLIED` pins what an action does not give. The unit tests of the
evaluator check the index; these check that the routes honor it.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from server.services.security.role_permission_evaluator import IMPLIED_ACTIONS
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.api.roles.conftest import Grants
from tests.api.roles.world import World
from tests.factories.request.classroom_request_factory import (
    ClassroomRequestFactory,
)

Action = BuildingAction | ClassroomAction


@dataclass(frozen=True)
class Probe:
    """A request that takes `action` on building A (or classroom_a)."""

    method: str
    url: Callable[[World], str]
    on_building: bool = False
    body: Callable[[World], Any] | None = None
    ok: int = 200


def _classroom_body(w: World) -> Any:
    factory = ClassroomRequestFactory(group=w.building_a.get_main_group())
    return jsonable_encoder(
        factory.create_input(building_id=must_be_int(w.building_a.id), group_ids=[])
    )


READ_CLASSROOM = Probe("GET", lambda w: f"/classrooms/{w.classroom_a.id}")
READ_SUBJECT = Probe("GET", lambda w: f"/subjects/{w.subject_a.id}", on_building=True)
UPDATE_CLASSROOM = Probe(
    "PUT", lambda w: f"/classrooms/{w.classroom_a.id}", body=_classroom_body
)
DELETE_CLASSROOM = Probe("DELETE", lambda w: f"/classrooms/{w.classroom_a.id}", ok=204)
ALLOCATE_IN_CLASSROOM = Probe(
    "POST",
    lambda w: (
        "/occurrences/allocate-schedule"
        f"?schedule_id={w.class_a.schedules[0].id}&classroom_id={w.classroom_a.id}"
    ),
)

# (granted, implied, probe that takes `implied`)
IMPLICATIONS: list[tuple[Action, Action, Probe]] = [
    (BuildingAction.CREATE, BuildingAction.READ, READ_SUBJECT),
    (ClassroomAction.UPDATE, ClassroomAction.READ, READ_CLASSROOM),
    (ClassroomAction.DELETE, ClassroomAction.READ, READ_CLASSROOM),
    (ClassroomAction.DELETE, ClassroomAction.UPDATE, UPDATE_CLASSROOM),
    (ClassroomAction.ALLOCATE, ClassroomAction.READ, READ_CLASSROOM),
    (ClassroomAction.RESERVE, ClassroomAction.READ, READ_CLASSROOM),
    (ClassroomAction.REQUEST, ClassroomAction.READ, READ_CLASSROOM),
]

# (granted, probe of an action it does not imply)
NOT_IMPLIED: list[tuple[Action, Probe]] = [
    (ClassroomAction.READ, UPDATE_CLASSROOM),
    (ClassroomAction.UPDATE, DELETE_CLASSROOM),
    (ClassroomAction.RESERVE, ALLOCATE_IN_CLASSROOM),
    (ClassroomAction.ALLOCATE, UPDATE_CLASSROOM),
]


def _grant(grant: Grants, w: World, probe: Probe, action: Action) -> None:
    if probe.on_building:
        grant.building(w.building_a, [BuildingAction(action)])
    else:
        grant.classroom(w.classroom_a, [ClassroomAction(action)])


def _call(client: TestClient, w: World, probe: Probe) -> int:
    body = probe.body(w) if probe.body else None
    return int(client.request(probe.method, probe.url(w), json=body).status_code)


def test_every_implication_is_probed() -> None:
    declared = {
        (str(granted), str(implied))
        for granted, implieds in IMPLIED_ACTIONS.items()
        for implied in implieds
    }
    probed = {(str(granted), str(implied)) for granted, implied, _ in IMPLICATIONS}
    assert probed == declared


@pytest.mark.parametrize(
    ("granted", "implied", "probe"),
    [pytest.param(*row, id=f"{row[0]} implies {row[1]}") for row in IMPLICATIONS],
)
def test_implied(
    granted: Action,
    implied: Action,
    probe: Probe,
    world: World,
    role_client: TestClient,
    grant: Grants,
) -> None:
    _grant(grant, world, probe, granted)

    assert _call(role_client, world, probe) == probe.ok


@pytest.mark.parametrize(
    ("granted", "probe"),
    [
        pytest.param(granted, probe, id=f"{granted} does not give {probe.method}")
        for granted, probe in NOT_IMPLIED
    ],
)
def test_not_implied(
    granted: Action,
    probe: Probe,
    world: World,
    role_client: TestClient,
    grant: Grants,
) -> None:
    _grant(grant, world, probe, granted)

    assert _call(role_client, world, probe) == 403
