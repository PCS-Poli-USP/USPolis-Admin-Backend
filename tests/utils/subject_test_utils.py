
from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import SubjectRegister
from server.routes.subject_routes import SubjectCodeAlreadyExists

from tests.utils.default_values.test_subject_default_values import SubjectDefaultValues


def make_subject(code: str) -> Subject:
    subject = Subject(
        code=code,
        name=SubjectDefaultValues.NAME,
        professors=SubjectDefaultValues.PROFESSORS,
        type=SubjectDefaultValues.TYPE,
        class_credit=SubjectDefaultValues.CLASS_CREDIT,
        work_credit=SubjectDefaultValues.WORK_CREDIT,
        activation=SubjectDefaultValues.ACTIVATION
    )
    return subject


def make_subject_register_input() -> SubjectRegister:
    register = SubjectRegister(
        code=SubjectDefaultValues.CODE,
        name=SubjectDefaultValues.NAME,
        professors=SubjectDefaultValues.PROFESSORS,
        type=SubjectDefaultValues.TYPE,
        class_credit=SubjectDefaultValues.CLASS_CREDIT,
        work_credit=SubjectDefaultValues.WORK_CREDIT,
        activation=SubjectDefaultValues.ACTIVATION,
    )
    return register


async def add_subject(code: str) -> str:
    if await Subject.check_code_exists(code):
        raise SubjectCodeAlreadyExists(code)
    subject = make_subject(code)
    await subject.create()
    return str(subject.id)
