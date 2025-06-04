from httpx import Response
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom


def assert_get_classroom_response(response: Response, classroom: Classroom) -> None:
    """Assert that the GET response contains the expected data for a classroom response based on the classroom model."""
    data = response.json()
    assert data["id"] == classroom.id
    assert data["name"] == classroom.name
    assert data["floor"] == classroom.floor
    assert data["capacity"] == classroom.capacity
    assert data["audiovisual"] == classroom.audiovisual


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
        schedule = schedules[0]
        assert schedule["id"] == class_.schedules[0].id
        assert schedule["start_time"] == class_.schedules[0].start_time.isoformat()
        assert schedule["end_time"] == class_.schedules[0].end_time.isoformat()
        assert len(schedule["occurrences"]) > 0
