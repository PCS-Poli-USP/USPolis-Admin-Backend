from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.models.http.responses.permissions_response_models import PermissionResponse
from server.repositories.classroom_permission_repository import (
    ClassroomPermissionRepository,
)
from server.repositories.course_permission_repository import CoursePermissionRepository
from server.utils.enums.resources_enums import Resource


router = APIRouter(prefix="/permissions", tags=["Permissions"])

PermissionRepositoryType = (
    type[ClassroomPermissionRepository] | type[CoursePermissionRepository]
)

PERMISSION_REPOSITORY_MAP: dict[Resource, PermissionRepositoryType] = {
    Resource.COURSE: CoursePermissionRepository,
    Resource.CLASSROOM: ClassroomPermissionRepository,
}


@router.get("")
def get_permissions(
    resource: Resource,
    session: SessionDep,
) -> list[PermissionResponse]:
    repository = PERMISSION_REPOSITORY_MAP[resource]
    permissions = repository.get_all(session=session)
    return PermissionResponse.from_permissions(permissions, resource)


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


@router.put("/{permission_id}")
def update_permission(
    permission_id: int,
    input: PermissionUpdate,
    session: SessionDep,
) -> JSONResponse:
    repository = PERMISSION_REPOSITORY_MAP[input.resource]
    permission = repository.get_by_id(id=permission_id, session=session)
    permission = repository.update(permission=permission, input=input, session=session)  # type: ignore
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
