from sqlmodel import Session, select, col
from server.models.database.building_db_model import Building
from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from tests.utils.default_values.test_subject_default_values import SubjectDefaultValues


def make_subject(code: str, buildings: list[Building]) -> Subject:
    subject = Subject(
        buildings=buildings,
        code=code,
        name=SubjectDefaultValues.NAME,
        professors=SubjectDefaultValues.PROFESSORS,
        type=SubjectDefaultValues.TYPE,
        class_credit=SubjectDefaultValues.CLASS_CREDIT,
        work_credit=SubjectDefaultValues.WORK_CREDIT,
        activation=SubjectDefaultValues.ACTIVATION,
    )
    return subject


def make_subject_register_input(building_ids: list[int]) -> SubjectRegister:
    register = SubjectRegister(
        code=SubjectDefaultValues.CODE,
        name=SubjectDefaultValues.NAME,
        building_ids=building_ids,
        professors=SubjectDefaultValues.PROFESSORS,
        type=SubjectDefaultValues.TYPE,
        class_credit=SubjectDefaultValues.CLASS_CREDIT,
        work_credit=SubjectDefaultValues.WORK_CREDIT,
        activation=SubjectDefaultValues.ACTIVATION,
    )
    return register


def make_subject_update_input(building_ids: list[int]) -> SubjectUpdate:
    register = SubjectUpdate(
        code=SubjectDefaultValues.CODE,
        name=SubjectDefaultValues.NAME,
        building_ids=building_ids,
        professors=SubjectDefaultValues.PROFESSORS,
        type=SubjectDefaultValues.TYPE,
        class_credit=SubjectDefaultValues.CLASS_CREDIT,
        work_credit=SubjectDefaultValues.WORK_CREDIT,
        activation=SubjectDefaultValues.ACTIVATION,
    )
    return register


def create_subject(session: Session, code: str, buildings: list[Building]) -> int:
    """Create a default subject with code and buildings"""
    subject = make_subject(code, buildings)
    session.add(subject)
    session.commit()
    return subject.id  # type: ignore


def check_code_exists(db: Session, code: str) -> bool:
    statement = select(Subject).where(col(Subject.code) == code)
    result = db.exec(statement).first()
    return result is not None
