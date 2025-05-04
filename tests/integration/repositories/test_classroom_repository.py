from unittest.mock import MagicMock

from sqlmodel import Session
from server.models.database.user_db_model import User
from server.models.database.group_db_model import Group
from server.repositories.classroom_repository import ClassroomRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.request.classroom_request_factory import ClassroomRequestFactory


def test_classroom_repository_create(
    group: Group, user: User, mock_session: MagicMock
) -> None:
    """Test the **create** method of the ClassroomRepository.\n
    Tests:\n
    - classroom is created with the correct values\n
    - session.commit() is not called\n
    - classroom id is None
    """
    factory = ClassroomRequestFactory(group=group)
    input = factory.create_input()
    classroom = ClassroomRepository.create(
        input=input, creator=user, session=mock_session
    )

    mock_session.commit.assert_not_called()
    assert classroom.id is None
    assert classroom.name == input.name


def test_classroom_repository_get_all(
    group: Group, user: User, session: Session
) -> None:
    """Test **get_all** method of the ClassroomRepository.\n
    Tests:\n
    - number of classrooms get is correct\n
    - classrooms read are the same as the ones created\n
    """
    factory = ClassroomModelFactory(creator=user, group=group, session=session)
    old_classrooms = factory.create_many_default()
    classrooms = ClassroomRepository.get_all(session=session)

    assert len(classrooms) == len(old_classrooms)
    for classroom in classrooms:
        assert classroom in old_classrooms


def test_classroom_repository_get_by_id(
    group: Group, user: User, session: Session
) -> None:
    """Test the **get_by_id** method of the ClassroomRepository.\n
    Tests:\n
    - classrooms read are the same as the ones created\n
    """
    factory = ClassroomModelFactory(creator=user, group=group, session=session)
    classroom = factory.create_and_refresh()
    query = ClassroomRepository.get_by_id(id=must_be_int(classroom.id), session=session)
    assert query.name == classroom.name


def test_classroom_repository_get_by_ids(
    group: Group, user: User, session: Session
) -> None:
    """Test the **get_by_ids** method of the ClassroomRepository.\n
    Tests:\n
    - classrooms read are the same as the ones created\n
    """
    factory = ClassroomModelFactory(creator=user, group=group, session=session)
    classrooms = factory.create_many_default()
    factory.commit()
    factory.refresh_many(classrooms)
    ids = [must_be_int(classroom.id) for classroom in classrooms]
    query = ClassroomRepository.get_by_ids(ids=ids, session=session)

    assert len(query) == len(classrooms)
    for classroom in query:
        assert classroom.id in ids


def test_classroom_repository_get_by_name_and_building(
    group: Group, user: User, session: Session
) -> None:
    """Test the **get_by_name_and_building** method of the ClassroomRepository.\n
    Setup:\n
    - Create a classroom on a building\n
    - Get the classroom by name and building\n
    Tests:\n
    - Check if classroom name are same\n
    - Check if classroom id are same\n
    """
    factory = ClassroomModelFactory(creator=user, group=group, session=session)
    classroom = factory.create_and_refresh()
    query = ClassroomRepository.get_by_name_and_building(
        name=classroom.name, building=group.building, session=session
    )
    assert query.name == classroom.name
    assert query.id == classroom.id
