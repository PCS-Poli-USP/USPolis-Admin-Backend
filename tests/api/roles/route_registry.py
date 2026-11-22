"""Who can call each route of the API.

Every route of the app is classified here, and `test_route_guard.py` checks the
classification against the app: a route that is not in the registry, or whose
authentication does not match its class, fails the suite. When you add a
route, add a line here (see docs/dev/backend/permissions.md, "Como cada rota é
classificada").

Classes (`Kind`):
- PUBLIC: no login, by design.
- HEALTH: the `x-api-key` header (HEALTH_API_KEY).
- MOBILE: the Google token of the mobile app (`Authorization` or `idToken`).
- SELF: login is enough; the route only touches the logged user's own data.
- GLOBAL_READ: login is enough; global information (holidays, calendars...).
- RESTRICTED_ANY: a group or any role (the restricted gate), nothing else;
  global entities anyone in the restricted tier can create.
- OWNER: the creator of the object (or the user it belongs to), or an admin.
- OBJECT: the permission `action` on the `resource` of the object (or, for a
  listing, the objects listed are filtered by it).
- ADMIN: admins only. Every route under `/admin` is ADMIN.

`gap` names a known hole, fixed in phase 2 of the permission plan (see
KNOWN_GAPS). A route whose gap changes how it is authenticated (the route
should be MOBILE or ADMIN but is anonymous today) has its guard tests marked as
expected failures until the fix lands.
"""

from dataclasses import dataclass
from enum import StrEnum

from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.resources_enums import Resource


class Kind(StrEnum):
    PUBLIC = "public"
    HEALTH = "health"
    MOBILE = "mobile"
    SELF = "self"
    GLOBAL_READ = "global_read"
    RESTRICTED_ANY = "restricted_any"
    OWNER = "owner"
    OBJECT = "object"
    ADMIN = "admin"


class Tier(StrEnum):
    """How the app authenticates a route (detected from its dependencies)."""

    PUBLIC = "public"
    HEALTH = "health"
    MOBILE = "mobile"
    AUTHENTICATED = "authenticated"
    RESTRICTED = "restricted"
    ADMIN = "admin"


# The tiers each class can live in.
ALLOWED_TIERS: dict[Kind, frozenset[Tier]] = {
    Kind.PUBLIC: frozenset({Tier.PUBLIC}),
    Kind.HEALTH: frozenset({Tier.HEALTH}),
    Kind.MOBILE: frozenset({Tier.MOBILE}),
    Kind.SELF: frozenset({Tier.AUTHENTICATED}),
    Kind.GLOBAL_READ: frozenset({Tier.AUTHENTICATED}),
    Kind.RESTRICTED_ANY: frozenset({Tier.RESTRICTED}),
    Kind.OWNER: frozenset({Tier.AUTHENTICATED, Tier.RESTRICTED}),
    Kind.OBJECT: frozenset({Tier.AUTHENTICATED, Tier.RESTRICTED}),
    Kind.ADMIN: frozenset({Tier.ADMIN}),
}


@dataclass(frozen=True)
class Rule:
    kind: Kind
    resource: Resource | None = None
    action: BuildingAction | ClassroomAction | None = None
    gap: str | None = None


RouteKey = tuple[str, str]  # (method, path)

PUBLIC = Rule(Kind.PUBLIC)
HEALTH = Rule(Kind.HEALTH)
MOBILE = Rule(Kind.MOBILE)
SELF = Rule(Kind.SELF)
GLOBAL_READ = Rule(Kind.GLOBAL_READ)
RESTRICTED_ANY = Rule(Kind.RESTRICTED_ANY)
OWNER = Rule(Kind.OWNER)
ADMIN = Rule(Kind.ADMIN)


def building(action: BuildingAction, gap: str | None = None) -> Rule:
    return Rule(Kind.OBJECT, Resource.BUILDING, action, gap)


def classroom(action: ClassroomAction, gap: str | None = None) -> Rule:
    return Rule(Kind.OBJECT, Resource.CLASSROOM, action, gap)


def gap(rule: Rule, code: str) -> Rule:
    return Rule(rule.kind, rule.resource, rule.action, code)


KNOWN_GAPS: dict[str, str] = {}

# Every route under this prefix is ADMIN (the admin router authenticates them
# all with admin_authenticate), so they are not listed one by one.
ADMIN_PREFIX = "/admin"

# Only mounted in development (CONFIG.environment == "development").
DEV_ROUTES: dict[RouteKey, Rule] = {
    ("POST", "/dev/jupiter/scrape"): ADMIN,
    ("GET", "/dev/errors/uncaught"): ADMIN,
}

R = BuildingAction
C = ClassroomAction

ROUTE_REGISTRY: dict[RouteKey, Rule] = {
    # -- health
    ("GET", "/health"): HEALTH,
    ("GET", "/health/database"): HEALTH,
    ("POST", "/health/user-schedules/invalidate-expired"): HEALTH,
    # -- mobile app
    ("GET", "/mobile/forum/posts"): PUBLIC,
    ("POST", "/mobile/forum/posts"): MOBILE,
    ("DELETE", "/mobile/forum/posts/{post_id}"): MOBILE,
    ("POST", "/mobile/forum/report"): MOBILE,
    ("POST", "/mobile/forum/posts/{post_id}"): MOBILE,
    ("GET", "/mobile/forum/posts/{post_id}"): PUBLIC,
    ("POST", "/mobile/forum/posts/{post_id}/liked"): MOBILE,
    ("GET", "/mobile/classes"): PUBLIC,
    ("GET", "/mobile/institutional-events"): PUBLIC,
    ("PATCH", "/mobile/institutional-events"): MOBILE,
    ("POST", "/mobile/comments"): MOBILE,
    ("GET", "/mobile/comments"): ADMIN,
    ("POST", "/mobile/authentication"): MOBILE,
    ("POST", "/mobile/authentication/new-user"): MOBILE,
    # -- public
    ("GET", "/buildings"): PUBLIC,
    ("GET", "/classrooms"): PUBLIC,
    ("GET", "/classrooms/paginated/"): PUBLIC,
    ("GET", "/classrooms/full/"): PUBLIC,
    ("GET", "/subjects"): PUBLIC,
    ("GET", "/subjects/core"): PUBLIC,
    ("GET", "/subjects/actives"): PUBLIC,
    ("GET", "/classes"): PUBLIC,
    ("GET", "/classes/full/"): PUBLIC,
    ("GET", "/classes/subject/{subject_id}"): PUBLIC,
    ("GET", "/classes/building/{building_name:path}"): PUBLIC,
    ("GET", "/classes/comming"): PUBLIC,
    ("GET", "/reservations/exams"): PUBLIC,
    ("GET", "/reservations/exams/events"): PUBLIC,
    ("GET", "/reservations/exams/subjects/{subject_id}"): PUBLIC,
    ("GET", "/reservations/exams/classes/{class_id}"): PUBLIC,
    ("GET", "/reservations/events"): PUBLIC,
    ("GET", "/reservations/meetings"): PUBLIC,
    ("GET", "/reservations"): PUBLIC,
    ("GET", "/reservations/full/"): PUBLIC,
    ("GET", "/reservations/building/{building_name:path}"): PUBLIC,
    ("GET", "/occurrences/schedule/full/{schedule_id}"): PUBLIC,
    ("GET", "/occurrences/schedule/{schedule_id}"): PUBLIC,
    ("GET", "/allocations/events"): PUBLIC,
    ("GET", "/allocations/resources"): PUBLIC,
    ("GET", "/auth/get-tokens"): PUBLIC,
    ("GET", "/auth/refresh-token"): PUBLIC,
    ("POST", "/auth/logout"): PUBLIC,
    ("GET", "/courses"): PUBLIC,
    ("GET", "/courses/jupiter/inactive-courses"): PUBLIC,
    ("GET", "/courses/jupiter/active-courses"): PUBLIC,
    ("GET", "/courses/options"): PUBLIC,
    ("GET", "/curriculums"): PUBLIC,
    ("GET", "/curriculum_subjects/{curriculum_id}/subjects"): PUBLIC,
    ("GET", "/curriculum_subjects"): PUBLIC,
    ("GET", "/static/{file_path:path}"): PUBLIC,
    ("GET", "/api-key-links/{link_id}"): PUBLIC,
    ("POST", "/api-key-links/{link_id}/reveal"): PUBLIC,
    ("GET", "/search"): PUBLIC,
    ("POST", "/search/log"): PUBLIC,
    ("GET", "/search/documents/{doc_key}"): PUBLIC,
    # -- buildings
    ("GET", "/buildings/{building_id}"): GLOBAL_READ,
    ("GET", "/buildings/occupance_reports/{building_id}"): building(R.READ),
    # -- classrooms
    ("GET", "/classrooms/{id}"): classroom(C.READ),
    ("GET", "/classrooms/full/{id}"): GLOBAL_READ,
    ("GET", "/classrooms/with-conflict-count/{building_id}/{schedule_id}"): building(
        R.READ
    ),
    ("POST", "/classrooms/with-conflict-count/{building_id}"): building(R.READ),
    ("POST", "/classrooms"): building(R.CREATE),
    ("PUT", "/classrooms/{id}"): classroom(C.UPDATE),
    ("DELETE", "/classrooms/{id}"): classroom(C.DELETE),
    # -- subjects
    ("GET", "/subjects/{subject_id}"): building(R.READ),
    ("POST", "/subjects/crawl"): building(R.CREATE),
    ("PATCH", "/subjects/crawl"): building(R.UPDATE),
    ("POST", "/subjects"): building(R.CREATE),
    ("PUT", "/subjects/{subject_id}"): building(R.UPDATE),
    ("DELETE", "/subjects/{subject_id}"): building(R.UPDATE),
    # -- the logged user
    ("GET", "/users"): SELF,
    ("PATCH", "/users/notifications/email"): SELF,
    ("GET", "/users/my-buildings"): building(R.READ),
    ("GET", "/users/my-groups"): SELF,
    ("GET", "/users/my-subjects"): building(R.READ),
    ("GET", "/users/my-classes"): building(R.READ),
    ("GET", "/users/my-classrooms"): classroom(C.READ),
    ("GET", "/users/my-reservations"): classroom(C.READ),
    ("GET", "/users/my-access"): SELF,
    ("GET", "/users/my-solicitations"): SELF,
    ("GET", "/users/my-course"): SELF,
    ("GET", "/users/my-curriculum"): SELF,
    ("POST", "/users/my-curriculum"): SELF,
    ("GET", "/users/my-schedule"): SELF,
    ("GET", "/users/{building_id}"): building(R.READ),
    ("POST", "/feedbacks"): SELF,
    ("POST", "/reports"): SELF,
    ("POST", "/users/schedules/crawl"): SELF,
    ("POST", "/users/schedules"): SELF,
    ("PUT", "/users/schedules/{user_schedule_id}"): OWNER,
    ("DELETE", "/users/schedules/{user_schedule_id}"): OWNER,
    # -- global entities: any restricted user creates, the creator edits
    ("GET", "/holidays_categories"): GLOBAL_READ,
    ("GET", "/holidays_categories/{holiday_category_id}"): GLOBAL_READ,
    ("POST", "/holidays_categories"): RESTRICTED_ANY,
    ("PUT", "/holidays_categories/{holiday_category_id}"): OWNER,
    ("DELETE", "/holidays_categories/{holiday_category_id}"): OWNER,
    ("GET", "/holidays"): GLOBAL_READ,
    ("GET", "/holidays/{holiday_id}"): GLOBAL_READ,
    ("POST", "/holidays"): RESTRICTED_ANY,
    ("POST", "/holidays/many"): RESTRICTED_ANY,
    ("PUT", "/holidays/{holiday_id}"): OWNER,
    ("DELETE", "/holidays/{holiday_id}"): OWNER,
    ("GET", "/calendars"): GLOBAL_READ,
    ("GET", "/calendars/year/{year}"): GLOBAL_READ,
    ("GET", "/calendars/{calendar_id}"): GLOBAL_READ,
    ("POST", "/calendars"): RESTRICTED_ANY,
    ("PUT", "/calendars/{calendar_id}"): OWNER,
    ("DELETE", "/calendars/{calendar_id}"): OWNER,
    ("GET", "/institutional_events"): GLOBAL_READ,
    ("GET", "/institutional_events/{institutional_event_id}"): GLOBAL_READ,
    ("POST", "/institutional_events"): RESTRICTED_ANY,
    ("PUT", "/institutional_events/{institutional_event_id}"): OWNER,
    ("DELETE", "/institutional_events/{institutional_event_id}"): OWNER,
    # -- classes
    ("GET", "/classes/subjects"): GLOBAL_READ,
    ("GET", "/classes/{class_id}"): classroom(C.READ),
    ("GET", "/classes/{class_id}/full"): classroom(C.READ),
    ("POST", "/classes"): building(R.CREATE),
    ("PUT", "/classes/{class_id}"): classroom(C.UPDATE),
    ("DELETE", "/classes/{class_id}"): classroom(C.UPDATE),
    ("DELETE", "/classes/many/"): classroom(C.UPDATE),
    # -- reservations
    ("POST", "/reservations/exams"): classroom(C.RESERVE),
    ("PUT", "/reservations/exams/{id}"): classroom(C.RESERVE),
    ("POST", "/reservations/events"): classroom(C.RESERVE),
    ("PUT", "/reservations/events/{id}"): classroom(C.RESERVE),
    ("POST", "/reservations/meetings"): classroom(C.RESERVE),
    ("PUT", "/reservations/meetings/{id}"): classroom(C.RESERVE),
    ("GET", "/reservations/{reservation_id}/full"): classroom(C.READ),
    ("GET", "/reservations/{reservation_id}"): classroom(C.READ),
    ("PATCH", "/reservations/{reservation_id}/edit-occurrences"): classroom(C.RESERVE),
    ("DELETE", "/reservations/{reservation_id}"): classroom(C.RESERVE),
    # -- schedules and allocation
    ("PATCH", "/schedules/{schedule_id}/edit-occurrences"): classroom(C.UPDATE),
    ("POST", "/schedules/create-for-class/{class_id}"): classroom(C.UPDATE),
    ("POST", "/schedules/create-many-for-classes"): classroom(C.UPDATE),
    ("GET", "/occurrences"): building(R.READ),
    ("POST", "/occurrences/allocate-schedule"): classroom(C.ALLOCATE),
    ("POST", "/occurrences/allocate-schedule-many"): classroom(C.ALLOCATE),
    ("DELETE", "/occurrences/remove-schedule-allocation"): classroom(C.ALLOCATE),
    ("PATCH", "/allocations/events"): classroom(C.ALLOCATE),
    ("POST", "/allocations/reuse-options"): classroom(C.READ),
    ("POST", "/allocations/allocate-allocation-map"): classroom(C.ALLOCATE),
    ("GET", "/allocations_logs/{schedule_id}"): classroom(C.READ),
    ("GET", "/conflicts/building/{building_id}"): building(R.READ),
    # -- solicitations
    ("GET", "/solicitations"): classroom(C.RESERVE),
    ("GET", "/solicitations/pending"): classroom(C.RESERVE),
    ("POST", "/solicitations"): classroom(C.REQUEST),
    ("PUT", "/solicitations/{solicitation_id}"): OWNER,
    ("PATCH", "/solicitations/cancel/{solicitation_id}"): OWNER,
    ("PUT", "/solicitations/approve/{solicitation_id}"): classroom(C.RESERVE),
    ("PUT", "/solicitations/deny/{solicitation_id}"): classroom(C.RESERVE),
}


def rule_for(method: str, path: str) -> Rule | None:
    """The class of a route, or None when it is not classified."""
    key = (method, path)
    if key in ROUTE_REGISTRY:
        return ROUTE_REGISTRY[key]
    if key in DEV_ROUTES:
        return DEV_ROUTES[key]
    if path == ADMIN_PREFIX or path.startswith(ADMIN_PREFIX + "/"):
        return ADMIN
    return None
