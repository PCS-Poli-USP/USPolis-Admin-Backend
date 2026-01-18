from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.classroom_permission_repository_adapter import (
    ClassroomPermissionRepositoryDep,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.http.requests.classroom_permission_request_models import (
    ClassroomPermissionManyRegister,
    ClassroomPermissionRegister,
    ClassroomPermissionUpdate,
)
from server.models.http.responses.classroom_permission_response_models import (
    ClassroomPermissionByClassroomResponse,
    ClassroomPermissionByUserResponse,
    ClassroomPermissionResponse,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.user_repository import UserRepository
from server.utils.must_be_int import must_be_int


embed = Body(..., embed=True)

router = APIRouter(
    prefix="/classroom_permissions",
    tags=["Classrooms", "Permissions"],
)


@router.get("")
def get_all_permissions(
    repository: ClassroomPermissionRepositoryDep,
) -> list[ClassroomPermissionResponse]:
    permissions = repository.get_all()
    return ClassroomPermissionResponse.from_permissions(permissions)


@router.get("/classrooms")
def get_permissions_by_classrooms(
    repository: ClassroomRepositoryDep,
) -> list[ClassroomPermissionByClassroomResponse]:
    classrooms = repository.get_all_restricted(
        load=["building", "permissions.user", "permissions.given_by"]
    )
    return ClassroomPermissionByClassroomResponse.from_classrooms(classrooms)


@router.get("/users")
def get_permissions_by_users(
    user: UserDep,
    session: SessionDep,
) -> list[ClassroomPermissionByUserResponse]:
    users = UserRepository.get_all(
        session=session,
        load=[
            "classroom_permissions.classroom.building",
        ],
    )
    classrooms_ids_set: set[int] = set()
    if user.is_admin:
        classrooms = ClassroomRepository.get_all(session=session, load=[])
        classrooms_ids_set = {must_be_int(cls.id) for cls in classrooms}
    else:
        classrooms_ids_set = user.classrooms_ids_set()

    return ClassroomPermissionByUserResponse.from_users(users, classrooms_ids_set)


@router.post("")
def create_classroom_permission(
    input: ClassroomPermissionRegister, repository: ClassroomPermissionRepositoryDep
) -> JSONResponse:
    repository.create(input=input)
    return JSONResponse(
        content={"message": "Permissões criadas com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/many")
def create_many_classroom_permission(
    input: ClassroomPermissionManyRegister, repository: ClassroomPermissionRepositoryDep
) -> JSONResponse:
    repository.create_many(input=input)
    return JSONResponse(
        content={"message": "Múltiplas permissões criadas com sucesso!"},
        status_code=status.HTTP_201_CREATED,
    )


@router.patch("/{permission_id}")
def update_classroom_permission(
    permission_id: int,
    input: ClassroomPermissionUpdate,
    repository: ClassroomPermissionRepositoryDep,
) -> JSONResponse:
    repository.update(id=permission_id, input=input)
    return JSONResponse(content={"message": "Permissões atualizadas com sucesso!"})


@router.delete("/{permission_id}")
def delete_classroom_permission(
    permission_id: int, repository: ClassroomPermissionRepositoryDep
) -> JSONResponse:
    repository.delete(id=permission_id)
    return JSONResponse(
        content={"message": "Permissões removidas com sucesso!"},
        status_code=status.HTTP_200_OK,
    )
