from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.repositories.building_repository import BuildingRepository


def owned_building_ids(user: UserDep, session: SessionDep) -> list[int]:
    if not user.is_admin:
        return [building.id for building in user.buildings]  # type: ignore
    else:
        return [building.id for building in BuildingRepository.get_all(session=session)]  # type: ignore


OwnedBuildingIdsDep = Annotated[list[int], Depends(owned_building_ids)]
