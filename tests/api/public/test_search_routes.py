from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.event_db_model import Event
from server.models.database.meeting_db_model import Meeting
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.search_repository import SearchRepository
from server.utils.enums.reservation_status import ReservationStatus
from tests.factories.model.event_model_factory import EventModelFactory
from tests.factories.model.meeting_model_factory import MeetingModelFactory

URL_PREFIX = "/search"


@pytest.fixture(name="search_data")
def search_data_fixture(
    building: Building,
    subject: Subject,
    class_: Class,
    allocated_classroom: Classroom,
    session: Session,
) -> dict[str, Any]:
    """Known names for the standard building/classroom/subject/class (the class
    is allocated in the classroom), then rebuild the search index."""
    building.name = "Biênio"
    allocated_classroom.name = "B2-04"
    subject.code = "MAC0110"
    subject.name = "Cálculo Diferencial e Integral I"
    # Same person, with and without the crawler's "(R)" (in charge) marker.
    subject.professors = ["(R) João da Silva Pereira"]
    class_.professors = ["João da Silva Pereira"]
    session.add_all([building, allocated_classroom, subject, class_])
    session.commit()
    assert SearchRepository.refresh(session=session)
    return {
        "building": building,
        "classroom": allocated_classroom,
        "subject": subject,
        "class": class_,
    }


def _search(client: TestClient, **params: Any) -> dict[str, Any]:
    response = client.get(URL_PREFIX, params=params)
    assert response.status_code == status.HTTP_200_OK, response.text
    data: dict[str, Any] = response.json()
    return data


def _group(data: dict[str, Any], type_: str) -> dict[str, Any] | None:
    return next((g for g in data["groups"] if g["type"] == type_), None)


def _related_keys(data: dict[str, Any]) -> set[str]:
    return {i["doc_key"] for g in data["top"]["related"] for i in g["items"]}


class TestSearchMatching:
    def test_query_without_accents_finds_subject_and_its_class(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calculo")

        subject = search_data["subject"]
        assert data["top"]["doc_key"] == f"subject:{subject.id}"
        assert data["top"]["title"] == "MAC0110 - Cálculo Diferencial e Integral I"
        assert f"class:{search_data['class'].id}" in _related_keys(data)

    def test_typo_still_finds_subject(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calclo")

        subjects = _group(data, "subject")
        assert subjects is not None
        assert subjects["items"][0]["entity_id"] == str(search_data["subject"].id)

    def test_exact_subject_code_is_the_top_result(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="mac0110")

        assert data["top"]["doc_key"] == f"subject:{search_data['subject'].id}"

    def test_partial_professor_name_finds_a_single_professor(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="joao pereira")

        assert data["top"]["type"] == "professor"
        assert data["top"]["title"] == "João da Silva Pereira"
        assert data["top"]["entity_id"] == "joao-da-silva-pereira"
        professors = _group(data, "professor")
        assert professors is not None
        # "(R) João da Silva Pereira" and "João da Silva Pereira" are one doc.
        assert professors["total"] == 1
        related = _related_keys(data)
        assert f"class:{search_data['class'].id}" in related
        assert f"subject:{search_data['subject'].id}" in related

    def test_classroom_name_links_to_building_and_allocated_class(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="B2-04")

        assert data["top"]["doc_key"] == f"classroom:{search_data['classroom'].id}"
        assert data["top"]["subtitle"] == "Biênio"
        related = _related_keys(data)
        assert f"building:{search_data['building'].id}" in related
        assert f"class:{search_data['class'].id}" in related

    def test_building_name_without_accent_links_to_its_classrooms(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="bienio")

        assert data["top"]["doc_key"] == f"building:{search_data['building'].id}"
        assert f"classroom:{search_data['classroom'].id}" in _related_keys(data)


class TestSearchParameters:
    def test_types_filter_restricts_groups(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calculo", types=["class"])

        assert [g["type"] for g in data["groups"]] == ["class"]
        assert data["top"]["type"] == "class"

    def test_related_limit_zero_skips_expansion(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="calculo", related_limit=0)

        assert data["top"]["related"] == []

    def test_no_match_returns_empty_response(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="xyzwvqk")

        assert data == {"query": "xyzwvqk", "top": None, "groups": []}

    def test_query_with_only_symbols_returns_empty_response(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="!! &&")

        assert data["top"] is None
        assert data["groups"] == []

    @pytest.mark.parametrize("q", ["a", "x" * 101])
    def test_rejects_too_short_or_too_long_queries(
        self, public_client: TestClient, q: str
    ) -> None:
        response = public_client.get(URL_PREFIX, params={"q": q})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rejects_unknown_type(self, public_client: TestClient) -> None:
        response = public_client.get(
            URL_PREFIX, params={"q": "calculo", "types": "user"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSearchIndex:
    def test_doc_key_is_unique_across_entity_types(
        self, search_data: dict[str, Any], session: Session
    ) -> None:
        row = (
            session.connection()
            .execute(
                text(
                    "SELECT count(*) AS total, count(DISTINCT doc_key) AS uniq, "
                    "count(DISTINCT entity_type || entity_id) AS pairs "
                    "FROM search_document"
                )
            )
            .one()
        )

        assert row.total == row.uniq == row.pairs
        # Refreshing again (CONCURRENTLY needs the unique index) still works.
        assert SearchRepository.refresh(session=session)


class TestGetSearchDocument:
    def test_returns_document_with_related(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        classroom = search_data["classroom"]
        response = public_client.get(f"{URL_PREFIX}/documents/classroom:{classroom.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["doc_key"] == f"classroom:{classroom.id}"
        assert data["title"] == "B2-04"
        related = {i["doc_key"] for g in data["related"] for i in g["items"]}
        assert f"building:{search_data['building'].id}" in related
        assert f"class:{search_data['class'].id}" in related

    def test_same_numeric_id_of_another_type_is_another_document(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        subject = search_data["subject"]
        response = public_client.get(f"{URL_PREFIX}/documents/subject:{subject.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["type"] == "subject"

    def test_unknown_document_returns_404(
        self, public_client: TestClient, search_data: dict[str, Any]
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/documents/classroom:999999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture(name="reservation_data")
def reservation_data_fixture(
    search_data: dict[str, Any],
    admin_user: User,
    classroom: Classroom,
    event: Event,
    meeting: Meeting,
    session: Session,
) -> dict[str, Any]:
    """Approved event citing the subject code, a regular meeting, a monitoria
    booked as a meeting and a denied event; then rebuild the index."""
    event.reservation.title = "Monitoria MAC0110 de Cálculo"
    # Factories leave reservation schedules unallocated; approved ones have a room.
    event.reservation.schedule.classroom_id = classroom.id
    meeting.reservation.title = "Reunião do conselho do departamento"
    monitoring_meeting = MeetingModelFactory(
        classroom=classroom, creator=admin_user, session=session
    ).create_and_refresh()
    monitoring_meeting.reservation.title = "Monitoria de Física"
    denied_event = EventModelFactory(
        classroom=classroom, creator=admin_user, session=session
    ).create_and_refresh()
    denied_event.reservation.title = "Monitoria negada de Química"
    denied_event.reservation.status = ReservationStatus.DENIED
    session.add_all(
        [
            event.reservation,
            event.reservation.schedule,
            meeting.reservation,
            monitoring_meeting.reservation,
            denied_event.reservation,
        ]
    )
    session.commit()
    assert SearchRepository.refresh(session=session)
    return {
        **search_data,
        "event": event,
        "meeting": meeting,
        "monitoring_meeting": monitoring_meeting,
        "denied_event": denied_event,
        "reservation_classroom": classroom,
    }


class TestSearchReservations:
    def test_monitoria_finds_events_and_monitoria_meetings(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="monitoria", limit=20)

        keys = {i["doc_key"] for g in data["groups"] for i in g["items"]}
        event_id = reservation_data["event"].reservation_id
        monitoring_id = reservation_data["monitoring_meeting"].reservation_id
        assert f"reservation:{event_id}" in keys
        assert f"reservation:{monitoring_id}" in keys
        # Denied reservations are never indexed.
        denied_id = reservation_data["denied_event"].reservation_id
        assert f"reservation:{denied_id}" not in keys
        types = {g["type"] for g in data["groups"]}
        assert {"event", "meeting"} <= types

    def test_regular_meetings_are_not_indexed(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        data = _search(public_client, q="conselho departamento")

        meeting_id = reservation_data["meeting"].reservation_id
        keys = {i["doc_key"] for g in data["groups"] for i in g["items"]}
        assert f"reservation:{meeting_id}" not in keys

    def test_subject_code_in_title_links_reservation_to_subject(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        event_id = reservation_data["event"].reservation_id
        response = public_client.get(f"{URL_PREFIX}/documents/reservation:{event_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["type"] == "event"
        assert data["payload"]["subjects"][0]["code"] == "MAC0110"
        related = {i["doc_key"] for g in data["related"] for i in g["items"]}
        assert f"subject:{reservation_data['subject'].id}" in related

    def test_classroom_related_includes_its_reservations(
        self, public_client: TestClient, reservation_data: dict[str, Any]
    ) -> None:
        classroom = reservation_data["reservation_classroom"]
        response = public_client.get(
            f"{URL_PREFIX}/documents/classroom:{classroom.id}",
            params={"related_limit": 20},
        )

        related = {i["doc_key"] for g in response.json()["related"] for i in g["items"]}
        event_id = reservation_data["event"].reservation_id
        assert f"reservation:{event_id}" in related
