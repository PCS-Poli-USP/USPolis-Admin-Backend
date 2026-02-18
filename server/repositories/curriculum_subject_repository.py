from fastapi import HTTPException
from sqlmodel import Session, select

from server.models.database.curriculum_subject_db_model import CurriculumSubject
from server.models.database.user_db_model import User
from server.models.http.requests.curriculum_subject_request_models import CurriculumSubjectRegister, CurriculumSubjectUpdate

class CurriculumSubjectRepository:
    @staticmethod
    def get_by_id(id: int, session: Session) -> CurriculumSubject | None:
        statement = select(CurriculumSubject).where(CurriculumSubject.id == id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_by_curriculum_id(curriculum_id: int, session: Session) -> list[CurriculumSubject]:
        statement = select(CurriculumSubject).where(CurriculumSubject.curriculum_id == curriculum_id)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(session: Session) -> list[CurriculumSubject]:
        statement = select(CurriculumSubject)
        return list(session.exec(statement).all())

    @staticmethod
    def create(
        input: CurriculumSubjectRegister,
        user: User,
        session: Session,
    ) -> CurriculumSubject:
        curriculum_subject = CurriculumSubject(
            curriculum_id=input.curriculum_id,
            subject_id=input.subject_id,
            type=input.type,
            period=input.period 
        )
        session.add(curriculum_subject)
        session.flush()
        return curriculum_subject


    @staticmethod
    def update(
        id: int,
        input: CurriculumSubjectUpdate,
        user: User,
        session: Session,
    ) -> CurriculumSubject:

        curriculum_subject = CurriculumSubjectRepository.get_by_id(id=id, session=session)

        if not curriculum_subject:
            raise HTTPException(404, "Disciplina do currículo não encontrada")

        curriculum_subject.curriculum_id = input.curriculum_id
        curriculum_subject.subject_id = input.subject_id
        curriculum_subject.type = input.type
        curriculum_subject.period = input.period

        session.add(curriculum_subject)
        session.flush()
        return curriculum_subject


    @staticmethod
    def delete(id: int, session: Session) -> None:

        curriculum_subject = CurriculumSubjectRepository.get_by_id(id=id, session=session)

        if not curriculum_subject:
            raise HTTPException(404, "Disciplina do currículo não encontrada")

        session.delete(curriculum_subject)
