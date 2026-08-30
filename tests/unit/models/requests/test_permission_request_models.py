import pytest
from pydantic import ValidationError

from server.models.http.requests.permission_request_models import PermissionRegister
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.enums.resources_enums import Resource


def test_permission_register_requires_role_id() -> None:
    with pytest.raises(ValidationError):
        PermissionRegister(  # type: ignore[call-arg]
            resource=Resource.CLASSROOM,
            resource_id=-1,
            actions=[ClassroomAction.READ],
        )


def test_permission_register_accepts_all_resources_wildcard() -> None:
    permission = PermissionRegister(
        resource=Resource.CLASSROOM,
        resource_id=-1,
        actions=[ClassroomAction.READ],
        role_id=1,
    )

    assert permission.resource_id == -1


@pytest.mark.parametrize("resource_id", [0, -2])
def test_permission_register_rejects_invalid_resource_id(resource_id: int) -> None:
    with pytest.raises(ValidationError):
        PermissionRegister(
            resource=Resource.CLASSROOM,
            resource_id=resource_id,
            actions=[ClassroomAction.READ],
            role_id=1,
        )


def test_permission_register_rejects_empty_actions() -> None:
    with pytest.raises(ValidationError):
        PermissionRegister(
            resource=Resource.CLASSROOM,
            resource_id=-1,
            actions=[],
            role_id=1,
        )


def test_permission_register_deduplicates_actions() -> None:
    permission = PermissionRegister(
        resource=Resource.CLASSROOM,
        resource_id=-1,
        actions=[ClassroomAction.READ, ClassroomAction.READ],
        role_id=1,
    )

    assert permission.actions == [ClassroomAction.READ]


def test_permission_register_rejects_action_not_valid_for_resource() -> None:
    with pytest.raises(ValidationError):
        PermissionRegister(  # type: ignore[call-arg]
            resource=Resource.COURSE,
            resource_id=-1,
            actions=[ClassroomAction.ALLOCATE],
        )


def test_permission_register_accepts_action_valid_for_resource() -> None:
    permission = PermissionRegister(
        resource=Resource.CLASSROOM,
        resource_id=-1,
        actions=[ClassroomAction.ALLOCATE, ClassroomAction.RESERVE],
        role_id=1,
    )

    assert permission.actions == [ClassroomAction.ALLOCATE, ClassroomAction.RESERVE]


def test_permission_register_accepts_allocate_and_reserve_for_building() -> None:
    """BuildingAction includes ALLOCATE/RESERVE so a BuildingPermission can grant
    them across every classroom in the building via the building-classroom cascade."""
    permission = PermissionRegister(
        resource=Resource.BUILDING,
        resource_id=-1,
        actions=[ClassroomAction.ALLOCATE, ClassroomAction.RESERVE],
        role_id=1,
    )

    assert permission.actions == [ClassroomAction.ALLOCATE, ClassroomAction.RESERVE]
