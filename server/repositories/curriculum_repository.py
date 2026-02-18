from fastapi import HTTPException
from sqlmodel import Session, select

from server.models.database.curriculum_db_model import Curriculum
from server.models.database.user_db_model import User
from server.models.http.requests.curriculum_request_models import CurriculumRegister, CurriculumUpdate
from server.utils.must_be_int import must_be_int

class CurriculumRepository:

    @staticmethod
    def create(
        input: CurriculumRegister,
        user: User,
        session: Session,
    ) -> Curriculum:
        curriculum = Curriculum(
            course_id=input.course_id,
            AAC=input.AAC,
            AEX=input.AEX,
            updated_by_id=must_be_int(user.id),
            created_by_id=must_be_int(user.id),
            description=input.description,
        )
        session.add(curriculum)
        session.flush()
        return curriculum

    @staticmethod
    def get_by_id(id: int, session: Session) -> Curriculum | None:
        statement = select(Curriculum).where(Curriculum.id == id)
        return session.exec(statement).first()

    @staticmethod
    def get_all(session: Session) -> list[Curriculum]:
        statement = select(Curriculum)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        id: int,
        input: CurriculumUpdate,
        user: User,
        session: Session,
    ) -> Curriculum:

        curriculum = CurriculumRepository.get_by_id(id=id, session=session)

        if not curriculum:
            raise HTTPException(404, "Currículo não encontrado")

        curriculum.course_id = input.course_id
        curriculum.AAC = input.AAC
        curriculum.AEX = input.AEX
        curriculum.updated_by_id = must_be_int(user.id)
        curriculum.description = input.description

        session.add(curriculum)
        session.flush()
        return curriculum


    @staticmethod
    def delete(id: int, session: Session) -> None:

        curriculum = CurriculumRepository.get_by_id(id=id, session=session)

        if not curriculum:
            raise HTTPException(404, "Currículo não encontrado")

        session.delete(curriculum)
