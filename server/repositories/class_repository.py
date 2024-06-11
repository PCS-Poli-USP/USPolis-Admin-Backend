from sqlmodel import Session, col, select

from server.models.database.class_db_model import Class
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.repositories.subject_repository import SubjectRepository


class ClassRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Class]:
        statement = select(Class)
        classes = session.exec(statement).all()
        return list(classes)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Class:
        statement = select(Class).where(col(Class.id) == id)
        _class = session.exec(statement).one()
        return _class

    @staticmethod
    def create(*, input: ClassRegister, session: Session) -> Class:
        subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
        input_data = input.model_dump()
        class_fields = Class.model_fields.keys()
        class_data = {key: input_data[key] for key in class_fields if key in input_data}
        print(class_data)
        print(class_fields)
        new_class = Class(**class_data, subject=subject)
        session.add(new_class)
        session.commit()
        session.refresh(new_class)
        return new_class

    @staticmethod
    def update(*, id: int, input: ClassUpdate, session: Session) -> Class:
        updated_class = ClassRepository.get_by_id(id=id, session=session)
        input_data = input.model_dump(exclude_unset=True)
        for key, value in input_data.items():
            if hasattr(updated_class, key):
                setattr(updated_class, key, value)

        if input.subject_id:
            subject = SubjectRepository.get_by_id(id=input.subject_id, session=session)
            updated_class.subject = subject

        session.add(updated_class)
        session.commit()
        return updated_class

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        deleted_class = ClassRepository.get_by_id(id=id, session=session)
        session.delete(deleted_class)
        session.commit()
