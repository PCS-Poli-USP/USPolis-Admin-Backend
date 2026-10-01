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


def test_permission_register_rejects_action_not_valid_for_course() -> None:
    # role_id must be supplied here, or pydantic's own required-field check
    # raises ValidationError first - before the "action valid for resource"
    # model_validator this test means to exercise ever runs at all.
    with pytest.raises(ValidationError, match="Ação inválida para cursos"):
        PermissionRegister(
            resource=Resource.COURSE,
            resource_id=-1,
            actions=[ClassroomAction.ALLOCATE],
            role_id=1,
        )


def test_permission_register_rejects_action_not_valid_for_classroom() -> None:
    # ClassroomAction's own 6 values are a superset of every other
    # PermissionAction member, so no real action value can ever fail this
    # check via normal construction - model_construct() bypasses pydantic's
    # enum coercion so the validator can still be exercised directly.
    permission = PermissionRegister.model_construct(
        resource=Resource.CLASSROOM,
        resource_id=-1,
        actions=["bogus_action"],
        role_id=1,
    )

    with pytest.raises(ValueError, match="Ação inválida para recurso salas"):
        permission.check_action_resource_consistency()  # type: ignore[operator]


def test_permission_register_rejects_action_not_valid_for_building() -> None:
    # Same reasoning as the classroom case above - BuildingAction's values
    # are also a superset of every other PermissionAction member.
    permission = PermissionRegister.model_construct(
        resource=Resource.BUILDING,
        resource_id=-1,
        actions=["bogus_action"],
        role_id=1,
    )

    with pytest.raises(ValueError, match="Ação inválida para recurso prédios"):
        permission.check_action_resource_consistency()  # type: ignore[operator]


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
