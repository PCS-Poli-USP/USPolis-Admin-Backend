from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.database.curriculum_db_model import Curriculum
from server.models.database.curriculum_subject_db_model import CurriculumSubject
from server.models.database.subject_db_model import Subject
from server.models.http.requests.curriculum_request_models import CreateCurriculumByJupiterFinalRequest, CreateCurriculumByJupiterRequest, CurriculumRegister, CurriculumSubjectPreview, CurriculumUpdate
from server.repositories.curriculum_repository import CurriculumRepository
from server.services.jupiter_crawler.curriculum_crawler.crawler import JupiterCurriculumCrawler
from server.utils.enums.curriculum_subject_category_enum import CurriculumSubjectCategory
from server.utils.enums.curriculum_subject_type_enum import CurriculumSubjectType

embed = Body(..., embed=True)

router = APIRouter(prefix="/curriculums", tags=["Curriculums"])


@router.post("")
def create_curriculum(
    input: CurriculumRegister, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Create new curriculum"""

    try:
        CurriculumRepository.create(input=input, user=user, session=session)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Currículo criado com sucesso",
            },
        )
    except IntegrityError as e:
        session.rollback()

        if "uq_curriculum_course_description" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um currículo com essa descrição nesse curso",
            )

        if "uq_curriculum_codcur_codhab" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um currículo com esse codcur e codhab",
            )

        raise HTTPException(
            status_code=400,
            detail="Não foi possível criar o currículo",
        )
    
@router.post("/jupiter")
async def create_curriculum_by_jupiter(
    input: CreateCurriculumByJupiterFinalRequest,
    session: SessionDep,
    user: UserDep,
) -> JSONResponse:
    try:
        if user.id is None:
            raise HTTPException(status_code=401, detail="Usuário inválido")

        curriculum = Curriculum(
            course_id=input.course_id,
            codcur=input.codcur,
            codhab=input.codhab,
            description=input.description,
            AAC=input.AAC,
            AEX=input.AEX,
            created_by_id=user.id,
            updated_by_id=user.id,
        )

        session.add(curriculum)
        session.commit()
        session.refresh(curriculum)

        if curriculum.id is None:
            raise HTTPException(status_code=500, detail="Erro ao criar currículo")

        missing_subjects: list[CurriculumSubjectPreview] = []

        def add_subjects(
            subjects_list: list[CurriculumSubjectPreview],
            category: CurriculumSubjectCategory,
        ) -> None:
            for subj in subjects_list:
                statement = select(Subject).where(Subject.code == subj.subject_code)
                subject_db = session.exec(statement).first()

                if not subject_db or subject_db.id is None:
                    missing_subjects.append(subj)
                    continue

                if curriculum.id is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Não foi possível criar o currículo via Jupiter",
                    )

                curriculum_subject = CurriculumSubject(
                    curriculum_id=curriculum.id,
                    subject_id=subject_db.id,
                    category=category,
                    type=CurriculumSubjectType.SEMESTRAL,
                    period=subj.period,
                )

                session.add(curriculum_subject)

        add_subjects(input.mandatory, CurriculumSubjectCategory.MANDATORY)
        add_subjects(input.free, CurriculumSubjectCategory.FREE_ELECTIVE)
        add_subjects(input.elective, CurriculumSubjectCategory.TRACK_ELECTIVE)

        session.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Currículo criado via Jupiter com sucesso",
                "missing_subjects": [s.model_dump() for s in missing_subjects],
            },
        )

    except IntegrityError as e:
        session.rollback()

        if "uq_curriculum_course_description" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um currículo com essa descrição nesse curso",
            )

        if "uq_curriculum_codcur_codhab" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um currículo com esse codcur e codhab",
            )

        raise HTTPException(
            status_code=400,
            detail="Não foi possível criar o currículo",
        )
    
@router.post("/jupiter/preview")
async def preview_curriculum_by_jupiter(
    input: CreateCurriculumByJupiterRequest,
    session: SessionDep,
    user: UserDep,
) -> dict[str, Any]:
    crawler = JupiterCurriculumCrawler(input.codcur, input.codhab)
    general_info, mandatory, free, elective = await crawler.crawl_curriculum()

    return {
        "description": input.description,
        "AAC": general_info.AAC,
        "AEX": general_info.AEX,
        "mandatory": [s.model_dump() for s in mandatory],
        "free": [s.model_dump() for s in free],
        "elective": [s.model_dump() for s in elective],
    }

@router.put("/{curriculum_id}")
def update_curriculum(
    curriculum_id: int, input: CurriculumUpdate, session: SessionDep, user: UserDep,
) -> JSONResponse:
    """Update a curriculum by id"""

    try:
        CurriculumRepository.update(id=curriculum_id, input=input, user=user, session=session)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Currículo atualizado com sucesso",
            },
        )
    except IntegrityError as e:
        session.rollback()

        if "uq_curriculum_course_description" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um currículo com essa descrição nesse curso",
            )

        if "uq_curriculum_codcur_codhab" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Já existe um currículo com esse codcur e codhab",
            )

        raise HTTPException(
            status_code=400,
            detail="Não foi possível atualizar o currículo",
        )

@router.delete("/{curriculum_id}")
def delete_curriculum(
    curriculum_id: int, session: SessionDep
) -> JSONResponse:
    """Delete a curriculum by id"""
    CurriculumRepository.delete(id=curriculum_id, session=session)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Currículo removido com sucesso",
        },
    )