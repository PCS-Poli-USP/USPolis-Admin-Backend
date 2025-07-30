from typing import Any
from httpx import Response
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom


def assert_classroom_data(data: Any, classroom: Classroom) -> None:
    """Assert that the data contains the expected fields for a classroom."""
    assert data["id"] == classroom.id
    assert data["name"] == classroom.name
    assert data["floor"] == classroom.floor
    assert data["capacity"] == classroom.capacity
    assert data["audiovisual"] == classroom.audiovisual


def assert_get_classroom_response(response: Response, classroom: Classroom) -> None:
    """Assert that the GET response contains the expected data for a classroom response based on the classroom model."""
    data = response.json()
    assert_classroom_data(data, classroom)


def assert_get_classroom_response_list(
    response: Response, classrooms: list[Classroom]
) -> None:
    """Assert that the GET response contains a list of classrooms with the expected data."""
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(classrooms)
    for i in range(len(classrooms)):
        assert_classroom_data(data[i], classrooms[i])


def assert_classroom_schedule_data(data: Any, class_: Class) -> None:
    assert data["id"] == class_.schedules[0].id
    assert data["start_time"] == class_.schedules[0].start_time.isoformat()
    assert data["end_time"] == class_.schedules[0].end_time.isoformat()
    assert len(data["occurrences"]) > 0


def assert_get_classroom_full_response(
    response: Response, classroom: Classroom, class_: Class
) -> None:
    """Assert that the GET response contains the expected data for a classroom full response (a classroom response with schedules with occurrences).
    - **This not checks if the occurrences are correct, only that they exist.**
    - **This assumes that the classroom has only the standard class allocated on it**
    - **The standard class has only one schedule with occurrences.**

    """
    assert_get_classroom_response(response, classroom)
    data = response.json()
    schedules = data["schedules"]
    assert isinstance(schedules, list)
    if len(schedules) > 0:
        assert_classroom_schedule_data(schedules[0], class_)


def assert_get_classroom_full_response_list(
    response: Response, classrooms: list[Classroom], classes: list[Class]
) -> None:
    """Assert that the GET response contains a list of classrooms full response.
    - **This not checks if the occurrences are correct, only that they exist.**
    - **This assumes that the classrooms have only the standard class allocated on them**
    - **The standard class has only one schedule with occurrences.**
    """
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(classrooms)
    assert len(data) == len(classes)
    for i in range(len(classrooms)):
        classroom_data = data[i]
        assert_classroom_data(classroom_data, classrooms[i])
        schedules = classroom_data["schedules"]
        assert isinstance(schedules, list)
        if len(schedules) > 0:
            assert_classroom_schedule_data(schedules[0], classes[i])


def assert_create_classroom_response(response: Response, classroom: Classroom) -> None:
    """Assert that the create classroom response contains the expected data."""
    assert_get_classroom_response(response, classroom)


def assert_update_classroom_response(response: Response, classroom: Classroom) -> None:
    """Assert that the update classroom response contains the expected data."""
    assert_get_classroom_response(response, classroom)
