from pydantic import BaseModel

from server.services.security.access_scope import AccessScope, Grant
from server.utils.enums.actions_enums import (
    BuildingAction,
    ClassroomAction,
    PermissionAction,
)

# Every action a building or classroom grant can carry, by value, in a stable
# order (BuildingAction and ClassroomAction share most values).
SCOPED_ACTIONS: dict[str, PermissionAction] = {
    action.value: action for action in [*BuildingAction, *ClassroomAction]
}


class AccessGrantResponse(BaseModel):
    """Every id (`all`), or exactly `ids`."""

    all: bool
    ids: list[int]

    @classmethod
    def from_grant(cls, grant: Grant) -> "AccessGrantResponse":
        return cls(all=grant.all, ids=sorted(grant.ids))


class ActionScopeResponse(BaseModel):
    # Buildings the action is granted on (a role or a legacy group).
    buildings: AccessGrantResponse
    # Classrooms the action is granted on, building grants included.
    classrooms: AccessGrantResponse
    # Buildings with the action on the building or on any of its classrooms:
    # the buildings to offer in a building filter.
    visible_buildings: AccessGrantResponse


class UserAccessResponse(BaseModel):
    is_admin: bool
    # Keyed by action ("read", "update", "allocate", "reserve", ...).
    scopes: dict[str, ActionScopeResponse]

    @classmethod
    def from_scope(cls, *, is_admin: bool, scope: AccessScope) -> "UserAccessResponse":
        return cls(
            is_admin=is_admin,
            scopes={
                name: ActionScopeResponse(
                    buildings=AccessGrantResponse.from_grant(
                        scope.building_grant(action)
                    ),
                    classrooms=AccessGrantResponse.from_grant(
                        scope.classroom_grant(action)
                    ),
                    visible_buildings=AccessGrantResponse.from_grant(
                        scope.visible_building_grant(action)
                    ),
                )
                for name, action in SCOPED_ACTIONS.items()
            },
        )
