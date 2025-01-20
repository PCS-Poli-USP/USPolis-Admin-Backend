from fastapi import APIRouter, Body

from server.deps.session_dep import SessionDep
from server.models.http.responses.class_response_models import (
    ClassResponse,
    ClassFullResponse,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.class_repository import ClassRepository
from server.utils.must_be_int import must_be_int

embed = Body(..., embed=True)

router = APIRouter(prefix="/classes", tags=["Public", "Classes"])


@router.get("")
async def get_all_classes(session: SessionDep) -> list[ClassResponse]:
    """Get all classes"""
    classes = ClassRepository.get_all(session=session)
    return ClassResponse.from_class_list(classes)


@router.get("/full/")
async def get_all_classes_full(
    session: SessionDep,
) -> list[ClassFullResponse]:
    """Get all classes with schedules and occurrences"""
    classes = ClassRepository.get_all(session=session)
    return ClassFullResponse.from_class_list(classes)


@router.get("/subject/{subject_id}")
async def get_all_classes_by_subject(
    subject_id: int, session: SessionDep
) -> list[ClassResponse]:
    """Get all classes by subject"""
    classes = ClassRepository.get_all_on_subject(subject_id=subject_id, session=session)
    return ClassResponse.from_class_list(classes)


@router.get("/building/{building_name}")
async def get_all_classes_by_building_name(
    building_name: str, session: SessionDep
) -> list[ClassResponse]:
    """Get all classes by building name"""
    building = BuildingRepository.get_by_name(name=building_name, session=session)
    classes = ClassRepository.get_all_on_buildings(
        building_ids=[must_be_int(building.id)], session=session
    )
    return ClassResponse.from_class_list(classes)
