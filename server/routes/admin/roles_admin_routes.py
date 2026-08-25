from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.role_request_models import RoleRegister, RoleUpdate
from server.models.http.responses.role_response_models import RoleResponse
from server.repositories.role_repository import RoleRepository
from server.utils.enums.resources_enums import Resource


router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("")
def get_roles(
    session: SessionDep, resources: list[Resource] = Query([])
) -> list[RoleResponse]:
    roles = RoleRepository.get_all(session=session, resources=resources)
    return RoleResponse.from_roles(roles)


@router.get("/{role_id}")
def get_role(role_id: int, session: SessionDep) -> RoleResponse:
    role = RoleRepository.get_by_id(id=role_id, session=session)
    return RoleResponse.from_role(role)


@router.post("")
def create_role(
    input: RoleRegister, user: UserDep, session: SessionDep
) -> JSONResponse:
    role = RoleRepository.create(input=input, user=user, session=session)
    session.commit()
    session.refresh(role)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Cargo criado com sucesso", "id": role.id},
    )


@router.put("/{role_id}")
def update_role(
    role_id: int, input: RoleUpdate, user: UserDep, session: SessionDep
) -> JSONResponse:
    role = RoleRepository.update(id=role_id, input=input, user=user, session=session)
    session.commit()
    session.refresh(role)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Cargo atualizado com sucesso"},
    )


@router.delete("/{role_id}")
def delete_role(role_id: int, session: SessionDep) -> JSONResponse:
    RoleRepository.delete(id=role_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Cargo deletado com sucesso"},
    )
