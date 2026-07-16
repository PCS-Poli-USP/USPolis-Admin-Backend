from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.permission_request_models import (
    PermissionBatchRegister,
    PermissionRegister,
    PermissionUpdate,
)
from server.models.http.responses.permissions_response_models import PermissionResponse
from server.repositories.building_permission_repository import (
    BuildingPermissionRepository,
)
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.repositories.course_permission_repository import CoursePermissionRepository
from server.utils.enums.resources_enums import Resource
from server.utils.permissions_types import Permission


router = APIRouter(prefix="/permissions", tags=["Permissions"])

PermissionRepositoryType = (
    type[ClassroomPermissionRepository]
    | type[CoursePermissionRepository]
    | type[BuildingPermissionRepository]
)

PERMISSION_REPOSITORY_MAP: dict[Resource, PermissionRepositoryType] = {
    Resource.BUILDING: BuildingPermissionRepository,
    Resource.CLASSROOM: ClassroomPermissionRepository,
    Resource.COURSE: CoursePermissionRepository,
}


@router.get("")
def get_permissions(
    resource: Resource,
    session: SessionDep,
) -> list[PermissionResponse]:
    repository = PERMISSION_REPOSITORY_MAP[resource]
    permissions = repository.get_all(session=session)
    return PermissionResponse.from_permissions(permissions, resource)


@router.get("/all")
def get_all_permissions(
    session: SessionDep,
) -> list[PermissionResponse]:
    all_permissions: list[PermissionResponse] = []
    for resource, repository in PERMISSION_REPOSITORY_MAP.items():
        permissions = repository.get_all(session=session)
        all_permissions.extend(
            PermissionResponse.from_permissions(permissions, resource)
        )
    return all_permissions


@router.get("/{permission_id}")
def get_permission(
    permission_id: int,
    resource: Resource,
    session: SessionDep,
) -> PermissionResponse:
    repository = PERMISSION_REPOSITORY_MAP[resource]
    permission = repository.get_by_id(id=permission_id, session=session)
    return PermissionResponse.from_permission(permission, resource)


@router.post("")
def create_permission(
    input: PermissionRegister,
    user: UserDep,
    session: SessionDep,
) -> JSONResponse:
    repository = PERMISSION_REPOSITORY_MAP[input.resource]
    permission = repository.create(input=input, user=user, session=session)
    session.commit()
    session.refresh(permission)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Permissão criada com sucesso", "id": permission.id},
    )


@router.post("/batch")
def create_permissions_batch(
    input: PermissionBatchRegister,
    user: UserDep,
    session: SessionDep,
) -> JSONResponse:
    created_permissions: list[Permission] = []
    for permission_input in input.permissions:
        repository = PERMISSION_REPOSITORY_MAP[permission_input.resource]
        permission = repository.create(
            input=permission_input, user=user, session=session
        )
        created_permissions.append(permission)
    session.commit()

    for permission in created_permissions:
        session.refresh(permission)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"{len(created_permissions)} permissões criadas com sucesso",
            "ids": [permission.id for permission in created_permissions],
        },
    )


@router.put("/{permission_id}")
def update_permission(
    permission_id: int,
    input: PermissionUpdate,
    user: UserDep,
    session: SessionDep,
) -> JSONResponse:
    repository = PERMISSION_REPOSITORY_MAP[input.resource]
    permission = repository.get_by_id(id=permission_id, session=session)
    permission = repository.update(permission=permission, input=input, user=user, session=session)  # type: ignore
    session.commit()
    session.refresh(permission)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Permissão atualizada com sucesso"},
    )


@router.delete("/{permission_id}")
def delete_permission(
    permission_id: int,
    resource: Resource,
    session: SessionDep,
) -> JSONResponse:
    repository = PERMISSION_REPOSITORY_MAP[resource]
    repository.delete(id=permission_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Permissão removida com sucesso"},
    )
