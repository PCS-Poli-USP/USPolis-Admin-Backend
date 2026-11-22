"""Route guard: every route is classified, and authenticated as its class says.

Generated from `route_registry.ROUTE_REGISTRY` and `app.routes`, so a new route
is covered (or fails `test_every_route_is_classified`) without writing a test.

What is checked here is the door of each route: login, the restricted gate,
admin-only. Whether a logged user can act on a given object is checked by the
permission matrix.

Path parameters get fake values (`1`): authentication runs before the path,
query and body are validated, so 401/403 come before any 404 or 422.
"""

import re
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from server.app import app
from server.deps.authenticate import (
    admin_authenticate,
    authenticate,
    health_token_authenticate,
    restricted_authenticate,
)
from server.deps.google_auth_dep import (
    google_authorization_authenticate,
    google_id_token_authenticate,
)
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from tests.api.roles.conftest import Grants
from tests.api.roles.route_registry import (
    ALLOWED_TIERS,
    KNOWN_GAPS,
    ROUTE_REGISTRY,
    Kind,
    Rule,
    Tier,
    rule_for,
)


@dataclass(frozen=True)
class AppRoute:
    method: str
    path: str
    tier: Tier

    @property
    def id(self) -> str:
        return f"{self.method} {self.path}"

    @property
    def url(self) -> str:
        """The path with every parameter replaced by a fake value."""
        return re.sub(r"\{[^}]+\}", "1", self.path)


# Strongest first: a route that depends on admin_authenticate also depends on
# restricted_authenticate and authenticate.
_TIER_BY_DEPENDENCY: list[tuple[Any, Tier]] = [
    (admin_authenticate, Tier.ADMIN),
    (restricted_authenticate, Tier.RESTRICTED),
    (authenticate, Tier.AUTHENTICATED),
    (google_authorization_authenticate, Tier.MOBILE),
    (google_id_token_authenticate, Tier.MOBILE),
    (health_token_authenticate, Tier.HEALTH),
]


def _dependency_calls(route: APIRoute) -> set[Any]:
    calls: set[Any] = set()
    stack = [route.dependant]
    while stack:
        dependant = stack.pop()
        if dependant.call is not None:
            calls.add(dependant.call)
        stack.extend(dependant.dependencies)
    return calls


def detected_tier(route: APIRoute) -> Tier:
    """How the app authenticates `route`, from its dependency tree (router
    dependencies included)."""
    calls = _dependency_calls(route)
    for dependency, tier in _TIER_BY_DEPENDENCY:
        if dependency in calls:
            return tier
    return Tier.PUBLIC


def _app_routes() -> Iterator[AppRoute]:
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        tier = detected_tier(route)
        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            yield AppRoute(method=method, path=route.path, tier=tier)


APP_ROUTES = list(_app_routes())


def _rule(route: AppRoute) -> Rule:
    rule = rule_for(route.method, route.path)
    # Unclassified routes fail test_every_route_is_classified; here they are
    # treated as admin-only, the strictest guess, so they are still exercised.
    return rule if rule is not None else Rule(Kind.ADMIN)


def _params(*kinds: Kind) -> list[Any]:
    """The routes of these classes, as pytest params.

    A route with a known gap that changes how it is authenticated (its tier
    today is not one its class allows) is an expected failure until the gap is
    fixed. strict=True: once fixed, the xfail must be removed.
    """
    params = []
    for route in APP_ROUTES:
        rule = _rule(route)
        if rule.kind not in kinds:
            continue
        marks = []
        if rule.gap and route.tier not in ALLOWED_TIERS[rule.kind]:
            marks.append(
                pytest.mark.xfail(
                    strict=True, reason=f"{rule.gap}: {KNOWN_GAPS[rule.gap]}"
                )
            )
        params.append(pytest.param(route, id=route.id, marks=marks))
    return params


def _restricted_tier_params() -> list[Any]:
    return [
        pytest.param(route, id=route.id)
        for route in APP_ROUTES
        if route.tier == Tier.RESTRICTED
    ]


@pytest.fixture(autouse=True)
def offline_google_tokens() -> Generator[None, None, None]:
    """The mobile token check downloads Google's certificates before decoding
    the token. No certificate: every token is rejected, without the network."""
    with patch("google.oauth2.id_token._fetch_certs", return_value={}):
        yield


# -- the registry matches the app


def test_every_route_is_classified() -> None:
    missing = [
        route.id for route in APP_ROUTES if rule_for(route.method, route.path) is None
    ]
    assert not missing, (
        "Routes without a class in tests/api/roles/route_registry.py "
        f"(add one line per route): {missing}"
    )


def test_registry_has_no_stale_routes() -> None:
    app_keys = {(route.method, route.path) for route in APP_ROUTES}
    stale = [
        f"{method} {path}"
        for method, path in ROUTE_REGISTRY
        if (method, path) not in app_keys
    ]
    assert not stale, f"Registry entries with no route in the app: {stale}"


def test_known_gaps_are_registered() -> None:
    used = {rule.gap for rule in ROUTE_REGISTRY.values() if rule.gap}
    assert used <= set(KNOWN_GAPS), used - set(KNOWN_GAPS)


def test_object_rules_name_resource_and_action() -> None:
    incomplete = [
        f"{method} {path}"
        for (method, path), rule in ROUTE_REGISTRY.items()
        if (rule.kind == Kind.OBJECT)
        != (rule.resource is not None and rule.action is not None)
    ]
    assert not incomplete, incomplete


@pytest.mark.parametrize("route", _params(*Kind))
def test_route_is_authenticated_as_its_class(route: AppRoute) -> None:
    rule = _rule(route)
    assert route.tier in ALLOWED_TIERS[rule.kind], (
        f"{route.id} is classified {rule.kind}, but the app authenticates it as "
        f"{route.tier}"
    )


# -- the door of each route


@pytest.mark.parametrize(
    "route",
    _params(
        Kind.SELF,
        Kind.GLOBAL_READ,
        Kind.RESTRICTED_ANY,
        Kind.OWNER,
        Kind.OBJECT,
        Kind.ADMIN,
    ),
)
def test_requires_login(route: AppRoute, public_client: TestClient) -> None:
    response = public_client.request(route.method, route.url)
    assert response.status_code == 401, response.text


@pytest.mark.parametrize("route", _params(Kind.MOBILE))
def test_mobile_requires_the_app_token(
    route: AppRoute, public_client: TestClient
) -> None:
    # No Authorization header (a Bearer token there would go to the web
    # login first) and an invalid idToken.
    response = public_client.request(
        route.method, route.url, headers={"idToken": "invalid"}
    )
    assert response.status_code == 401, response.text


@pytest.mark.parametrize("route", _params(Kind.HEALTH))
def test_health_requires_the_api_key(
    route: AppRoute, public_client: TestClient
) -> None:
    response = public_client.request(
        route.method, route.url, headers={"x-api-key": "wrong"}
    )
    assert response.status_code == 401, response.text


@pytest.mark.parametrize("route", _restricted_tier_params())
def test_restricted_tier_needs_a_group_or_a_role(
    route: AppRoute, role_client: TestClient
) -> None:
    """`role_user` has no group and no role yet: only the gate answers."""
    response = role_client.request(route.method, route.url)
    assert response.status_code == 403, response.text


@pytest.mark.parametrize("route", _params(Kind.SELF, Kind.GLOBAL_READ))
def test_login_is_enough(route: AppRoute, role_client: TestClient) -> None:
    """A user with no group and no role passes the door (the fake ids and the
    empty body can still give 404 or 422)."""
    response = role_client.request(route.method, route.url)
    assert response.status_code not in (401, 403), response.text


@pytest.mark.parametrize("route", _params(Kind.RESTRICTED_ANY))
def test_any_role_passes_the_restricted_gate(
    route: AppRoute,
    role_client: TestClient,
    grant: Grants,
    classroom_a: Classroom,
) -> None:
    grant.classroom(classroom_a, [ClassroomAction.READ])
    response = role_client.request(route.method, route.url)
    assert response.status_code not in (401, 403), response.text


@pytest.fixture
def maximal_role(
    grant: Grants,
    building_a: Building,
    building_b: Building,
    classroom_a: Classroom,
    classroom_b: Classroom,
) -> None:
    """The most a role can hold: every honored wildcard and every action on
    both buildings and their classrooms."""
    grant.building(None, list(BuildingAction))
    grant.classroom(None, list(ClassroomAction))
    for building in (building_a, building_b):
        grant.building(building, list(BuildingAction))
    for classroom in (classroom_a, classroom_b):
        grant.classroom(classroom, list(ClassroomAction))


@pytest.mark.parametrize("route", _params(Kind.ADMIN))
def test_admin_only_even_for_the_maximal_role(
    route: AppRoute, role_client: TestClient, maximal_role: None
) -> None:
    response = role_client.request(route.method, route.url)
    assert response.status_code == 403, response.text
