from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from server.deps.session_dep import SessionDep
from server.models.http.requests.group_request_models import GroupRegister, GroupUpdate
from server.models.http.responses.group_response_models import GroupResponse
from server.repositories.group_repository import GroupRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("")
def get_groups(session: SessionDep) -> list[GroupResponse]:
    """
    Get all groups
    """
    groups = GroupRepository.get_all(session=session)
    return GroupResponse.from_group_list(groups)


@router.get("/{group_id}")
def get_group(
    group_id: int,
    session: SessionDep,
) -> GroupResponse:
    """
    Get a group by id
    """
    group = GroupRepository.get_by_id(id=group_id, session=session)
    return GroupResponse.from_group(group)


@router.post("")
def create_group(
    input: GroupRegister,
    session: SessionDep,
) -> JSONResponse:
    """
    Create a group
    """
    try:
        GroupRepository.create(input=input, session=session)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise GroupAlreadyExists(name=input.name)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Grupo criado com sucesso",
        },
    )


@router.put("/{group_id}")
def update_group(
    group_id: int,
    input: GroupUpdate,
    session: SessionDep,
) -> JSONResponse:
    """
    Update a group by id
    """
    try:
        GroupRepository.update(id=group_id, input=input, session=session)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise GroupAlreadyExists(name=input.name)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Grupo atualizado com sucesso",
        },
    )


@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    session: SessionDep,
) -> JSONResponse:
    """
    Delete a group by id
    """
    GroupRepository.delete(id=group_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Grupo deletado com sucesso",
        },
    )


class GroupAlreadyExists(HTTPException):
    def __init__(self, name: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Grupo com o nome {name} já existe no prédio informado.",
        )
