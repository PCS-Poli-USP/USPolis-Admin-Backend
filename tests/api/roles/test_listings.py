"""Listings: the OBJECT routes that list instead of acting on one object.

`LISTINGS` has one line per such route (test_permission_matrix.LISTINGS names
the same routes). Each one creates an object of building A and one of building
B, and checks which of the two the user gets, per variant:

| variant   | what role_user holds                                        | lists  |
|-----------|-------------------------------------------------------------|--------|
| exact     | the action on building A (classroom_a for classroom lists)  | A      |
| none      | nothing                                                     | nothing |
| classroom | the action on classroom_a only (building lists: belonging)  | A      |
| cascade   | the action on building A (classroom lists)                  | A      |
| wildcard  | the action on everything (-1)                               | A and B for READ, nothing for admin-only actions |
| legacy    | a member of building A's main group, no role                | A      |

Lists are compared only on the two objects created, so other rows in the
database do not matter.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi.testclient import TestClient

from server.services.security.role_permission_evaluator import (
    GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS,
)
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.api.roles.conftest import Grants
from tests.api.roles.route_registry import ROUTE_REGISTRY, Rule
from tests.api.roles.test_permission_matrix import LISTINGS as LISTING_ROUTES
from tests.api.roles.world import World

Ids = set[int]


def _ids(body: Any) -> Ids:
    rows = body["data"] if isinstance(body, dict) else body
    return {row["id"] for row in rows}


def _occurrences(w: World) -> tuple[Ids, Ids]:
    def of(class_: Any) -> Ids:
        return {must_be_int(o.id) for o in class_.schedules[0].occurrences}

    a = w.allocated_class(w.class_a, w.classroom_a)
    b = w.allocated_class(w.class_b, w.classroom_b)
    return of(a), of(b)


def _reservations(w: World) -> tuple[Ids, Ids]:
    _, a = w.meeting_reservation(w.classroom_a)
    _, b = w.meeting_reservation(w.classroom_b)
    return {must_be_int(a.id)}, {must_be_int(b.id)}


def _solicitations(w: World) -> tuple[Ids, Ids]:
    a = w.solicitation(w.building_a, w.classroom_a)
    b = w.solicitation(w.building_b, w.classroom_b)
    return {must_be_int(a.id)}, {must_be_int(b.id)}


def _pair(a: Any, b: Any) -> tuple[Ids, Ids]:
    return {must_be_int(a.id)}, {must_be_int(b.id)}


@dataclass(frozen=True)
class Listing:
    path: str
    make: Callable[[World], tuple[Ids, Ids]]
    rule: Rule = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule", ROUTE_REGISTRY[("GET", self.path)])


LISTINGS: list[Listing] = [
    Listing("/occurrences", _occurrences),
    Listing("/users/my-buildings", lambda w: _pair(w.building_a, w.building_b)),
    Listing("/users/my-subjects", lambda w: _pair(w.subject_a, w.subject_b)),
    Listing("/users/my-classes", lambda w: _pair(w.class_a, w.class_b)),
    Listing("/users/my-classrooms", lambda w: _pair(w.classroom_a, w.classroom_b)),
    Listing("/users/my-reservations", _reservations),
    Listing("/solicitations", _solicitations),
    Listing("/solicitations/pending", _solicitations),
]

VARIANTS = ("exact", "none", "classroom", "cascade", "wildcard", "legacy")


def _expected(listing: Listing, variant: str) -> str | None:
    """ "A", "AB", "" (nothing), or None when the variant does not apply."""
    on_classroom = listing.rule.resource == Resource.CLASSROOM
    if variant in ("exact", "legacy"):
        return "A"
    if variant == "none":
        return ""
    if variant == "classroom":
        return None if on_classroom else "A"
    if variant == "cascade":
        return "A" if on_classroom else None
    if variant == "wildcard":
        return "" if listing.rule.action in GLOBAL_WILDCARD_ADMIN_ONLY_ACTIONS else "AB"
    raise ValueError(variant)


def _cases() -> list[Any]:
    return [
        pytest.param(listing, variant, expected, id=f"{listing.path} [{variant}]")
        for listing in LISTINGS
        for variant in VARIANTS
        if (expected := _expected(listing, variant)) is not None
    ]


def _hold(variant: str, listing: Listing, w: World, grant: Grants) -> None:
    action = listing.rule.action
    assert action is not None
    on_classroom = listing.rule.resource == Resource.CLASSROOM
    if variant == "exact":
        if on_classroom:
            grant.classroom(w.classroom_a, [ClassroomAction(action)])
        else:
            grant.building(w.building_a, [BuildingAction(action)])
    elif variant == "classroom":
        grant.classroom(w.classroom_a, [ClassroomAction(action)])
    elif variant == "cascade":
        grant.building(w.building_a, [BuildingAction(action)])
    elif variant == "wildcard":
        if on_classroom:
            grant.classroom(None, [ClassroomAction(action)])
        else:
            grant.building(None, [BuildingAction(action)])
    elif variant == "legacy":
        grant.legacy_group(w.building_a)


def test_every_listing_route_is_tested() -> None:
    assert {("GET", listing.path) for listing in LISTINGS} == set(LISTING_ROUTES)


@pytest.mark.parametrize(("listing", "variant", "expected"), _cases())
def test_listing(
    listing: Listing,
    variant: str,
    expected: str,
    world: World,
    role_client: TestClient,
    grant: Grants,
) -> None:
    ids_a, ids_b = listing.make(world)
    assert ids_a and ids_b and not ids_a & ids_b
    _hold(variant, listing, world, grant)

    response = role_client.get(listing.path)

    assert response.status_code == 200, response.text
    wanted = (ids_a if "A" in expected else set()) | (
        ids_b if "B" in expected else set()
    )
    assert _ids(response.json()) & (ids_a | ids_b) == wanted
