"""Which buildings and classrooms a user can act on, for listing and scoping.

The permission checkers answer "can this user do X on this object?". This
module answers the listing question, "on which objects can this user do X?",
with the same rules:

- an admin can act on everything;
- roles grant actions on specific buildings or classrooms, or on all of them
  through a wildcard (see `PermissionIndex.ids_with_permission`);
- a building grant cascades to every classroom in the building;
- legacy groups still grant their buildings and classrooms, for any action.

The group part lives only in the `_legacy_group_*` methods: delete them when
`Group` is retired (see docs/PERMISSIONS.md).
"""

from dataclasses import dataclass

from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import ClassroomAction, PermissionAction
from server.utils.enums.resources_enums import Resource


@dataclass(frozen=True, slots=True)
class Grant:
    """Ids a user can act on: every id (`all`), or exactly `ids`."""

    all: bool
    ids: frozenset[int]

    @classmethod
    def everything(cls) -> "Grant":
        return cls(all=True, ids=frozenset())


class AccessScope:
    """Resolves, per action, the buildings and classrooms a user can act on.

    Build one per request (see `AccessScopeDep`); results are cached per action.
    """

    def __init__(
        self, *, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        self.user = user
        self.session = session
        self.index = permission_index
        self._buildings: dict[str, Grant] = {}
        self._classrooms: dict[str, Grant] = {}
        self._visible_buildings: dict[str, Grant] = {}

    # -- grants (all flag + ids) :

    def building_grant(self, action: PermissionAction) -> Grant:
        """Buildings granted for `action`, by a role or a group."""
        if action not in self._buildings:
            role_ids = self.index.ids_with_permission(
                resource=Resource.BUILDING, action=action
            )
            if role_ids is None:
                grant = Grant.everything()
            else:
                grant = Grant(
                    all=False, ids=role_ids | self._legacy_group_building_ids()
                )
            self._buildings[action] = grant
        return self._buildings[action]

    def classroom_grant(self, action: PermissionAction) -> Grant:
        """Classrooms granted for `action`: direct grants, the classrooms of
        granted buildings (cascade), and the classrooms of the user's groups."""
        if action not in self._classrooms:
            classroom_ids = self.index.ids_with_permission(
                resource=Resource.CLASSROOM, action=action
            )
            building_ids = self.index.ids_with_permission(
                resource=Resource.BUILDING, action=action
            )
            if classroom_ids is None or building_ids is None:
                grant = Grant.everything()
            else:
                grant = Grant(
                    all=False,
                    ids=classroom_ids
                    | self._classroom_ids_in_buildings(building_ids)
                    | self._legacy_group_classroom_ids(),
                )
            self._classrooms[action] = grant
        return self._classrooms[action]

    def visible_building_grant(self, action: PermissionAction) -> Grant:
        """Buildings where the user can do `action` on the building itself or
        on at least one of its classrooms (e.g. the buildings to offer in a
        building filter)."""
        if action not in self._visible_buildings:
            buildings = self.building_grant(action)
            classrooms = self.classroom_grant(action)
            if buildings.all or classrooms.all:
                grant = Grant.everything()
            else:
                grant = Grant(
                    all=False,
                    ids=buildings.ids | self._building_ids_of(classrooms.ids),
                )
            self._visible_buildings[action] = grant
        return self._visible_buildings[action]

    # -- concrete ids (for SQL `IN` filters) :

    def building_ids(self, action: PermissionAction) -> list[int]:
        return self._concrete_buildings(self.building_grant(action))

    def classroom_ids(self, action: PermissionAction) -> list[int]:
        grant = self.classroom_grant(action)
        if grant.all:
            return list(self.session.exec(select(Classroom.id)).all())  # type: ignore[arg-type]
        return sorted(grant.ids)

    def visible_building_ids(self, action: PermissionAction) -> list[int]:
        return self._concrete_buildings(self.visible_building_grant(action))

    def readable_building_ids(self) -> list[int]:
        """The buildings to list for the user: those they can read, or read a
        classroom in (what the legacy `user.buildings` used to scope)."""
        return self.visible_building_ids(ClassroomAction.READ)

    # -- helpers :

    def _concrete_buildings(self, grant: Grant) -> list[int]:
        if grant.all:
            return list(self.session.exec(select(Building.id)).all())  # type: ignore[arg-type]
        return sorted(grant.ids)

    def _classroom_ids_in_buildings(self, building_ids: frozenset[int]) -> set[int]:
        if not building_ids:
            return set()
        statement = select(Classroom.id).where(
            col(Classroom.building_id).in_(building_ids)
        )
        return {id for id in self.session.exec(statement).all() if id is not None}

    def _building_ids_of(self, classroom_ids: frozenset[int]) -> set[int]:
        if not classroom_ids:
            return set()
        statement = (
            select(Classroom.building_id)
            .where(col(Classroom.id).in_(classroom_ids))
            .distinct()
        )
        return set(self.session.exec(statement).all())

    def _legacy_group_building_ids(self) -> frozenset[int]:
        # Legacy groups: the buildings of the user's groups (user.buildings).
        return frozenset(self.user.buildings_ids_set())

    def _legacy_group_classroom_ids(self) -> frozenset[int]:
        # Legacy groups: a group's classrooms, or a main group's whole building.
        return frozenset(self.user.classrooms_ids_set())
