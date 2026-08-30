from datetime import date

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.models.http.requests.schedule_request_models import (
    ScheduleUpdateOccurrences,
)
from server.repositories.reservation_repository import (
    ReservationAlreadyDeleted,
    ReservationNotFound,
    ReservationRepository,
)
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.request.reservation_request_factory import (
    ReservationRequestFactory,
)


def _create_reservation(
    *, admin_user: User, classroom: Classroom, session: Session, allocate: bool = True
) -> Reservation:
    input = ReservationRequestFactory(
        reservation_type=ReservationType.MEETING, classroom=classroom
    ).create_input()
    reservation = ReservationRepository.create(
        creator=admin_user, input=input, classroom=classroom, session=session,
        allocate=allocate,
    )
    session.commit()
    session.refresh(reservation)
    return reservation


class TestCreate:
    def test_creates_a_reservation_with_a_schedule(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).create_input()

        reservation = ReservationRepository.create(
            creator=admin_user, input=input, classroom=classroom, session=session
        )
        session.commit()
        session.refresh(reservation)

        assert reservation.title == input.title
        assert reservation.status == ReservationStatus.APPROVED
        assert reservation.schedule.classroom_id == classroom.id

    def test_allocate_false_leaves_the_reservation_pending(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).create_input()

        reservation = ReservationRepository.create(
            creator=admin_user,
            input=input,
            classroom=classroom,
            session=session,
            allocate=False,
        )
        session.commit()
        session.refresh(reservation)

        assert reservation.status == ReservationStatus.PENDING
        assert reservation.schedule.allocated is False


class TestGetById:
    def test_returns_the_matching_reservation(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        found = ReservationRepository.get_by_id(
            id=must_be_int(reservation.id), session=session
        )

        assert found.id == reservation.id

    def test_raises_when_reservation_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ReservationNotFound):
            ReservationRepository.get_by_id(id=999999, session=session)


class TestGetByIdOnBuildings:
    def test_returns_the_reservation_when_its_building_matches(
        self,
        admin_user: User,
        classroom: Classroom,
        building: Building,
        session: Session,
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        found = ReservationRepository.get_by_id_on_buildings(
            id=must_be_int(reservation.id),
            building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert found.id == reservation.id

    def test_raises_when_the_building_does_not_match(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        with pytest.raises(ReservationNotFound):
            ReservationRepository.get_by_id_on_buildings(
                id=must_be_int(reservation.id),
                building_ids=[999999],
                session=session,
            )


class TestGetByIdOnClassrooms:
    def test_returns_the_reservation_when_its_classroom_matches(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        found = ReservationRepository.get_by_id_on_classrooms(
            id=must_be_int(reservation.id),
            classroom_ids=[must_be_int(classroom.id)],
            session=session,
        )

        assert found.id == reservation.id

    def test_raises_when_the_classroom_does_not_match(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        with pytest.raises(ReservationNotFound):
            ReservationRepository.get_by_id_on_classrooms(
                id=must_be_int(reservation.id),
                classroom_ids=[999999],
                session=session,
            )

    def test_does_not_return_a_different_reservation_in_the_same_classroom(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        first = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )
        second = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        found = ReservationRepository.get_by_id_on_classrooms(
            id=must_be_int(first.id),
            classroom_ids=[must_be_int(classroom.id)],
            session=session,
        )

        assert found.id == first.id
        assert found.id != second.id


class TestGetAll:
    def test_returns_reservations_active_today_by_default(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        reservations = ReservationRepository.get_all(
            session=session, interval=QueryInterval()
        )

        assert reservation.id in [r.id for r in reservations]

    def test_excludes_reservations_outside_the_start_end_interval(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        reservations = ReservationRepository.get_all(
            session=session,
            interval=QueryInterval(start=date(1999, 1, 1), end=date(1999, 12, 31)),
        )

        assert reservation.id not in [r.id for r in reservations]


class TestGetAllOnBuildings:
    def test_returns_reservations_of_the_given_building(
        self,
        admin_user: User,
        classroom: Classroom,
        building: Building,
        session: Session,
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        reservations = ReservationRepository.get_all_on_buildings(
            building_ids=[must_be_int(building.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert reservation.id in [r.id for r in reservations]

    def test_excludes_reservations_of_other_buildings(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        reservations = ReservationRepository.get_all_on_buildings(
            building_ids=[999999], session=session, interval=QueryInterval()
        )

        assert reservation.id not in [r.id for r in reservations]


class TestGetAllOnClassrooms:
    def test_returns_reservations_of_the_given_classroom(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        reservations = ReservationRepository.get_all_on_classrooms(
            classroom_ids=[must_be_int(classroom.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert reservation.id in [r.id for r in reservations]

    def test_excludes_reservations_of_other_classrooms(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        reservations = ReservationRepository.get_all_on_classrooms(
            classroom_ids=[999999], session=session, interval=QueryInterval()
        )

        assert reservation.id not in [r.id for r in reservations]


class TestUpdate:
    def test_updates_title_and_reason(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        factory = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        )
        update_input = factory.update_input(
            title="Reunião atualizada", reason="Novo motivo"
        )

        updated = ReservationRepository.update(
            id=must_be_int(reservation.id),
            input=update_input,
            classroom=classroom,
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        assert updated.title == "Reunião atualizada"
        assert updated.reason == "Novo motivo"

    def test_raises_when_reservation_does_not_exist(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        update_input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).update_input()

        with pytest.raises(ReservationNotFound):
            ReservationRepository.update(
                id=999999,
                input=update_input,
                classroom=classroom,
                user=admin_user,
                session=session,
            )

    def test_moving_to_a_different_classroom_reallocates_the_schedule(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )

        update_input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=other_classroom
        ).update_input()

        updated = ReservationRepository.update(
            id=must_be_int(reservation.id),
            input=update_input,
            classroom=other_classroom,
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        assert updated.schedule.classroom_id == other_classroom.id


class TestDelete:
    def test_hard_deletes_a_reservation_without_a_solicitation(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )
        reservation_id = must_be_int(reservation.id)

        ReservationRepository.delete(id=reservation_id, user=admin_user, session=session)
        session.commit()

        with pytest.raises(ReservationNotFound):
            ReservationRepository.get_by_id(id=reservation_id, session=session)

    def test_soft_deletes_a_reservation_with_a_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )
        reservation.status = ReservationStatus.PENDING
        solicitation = Solicitation(
            capacity=10,
            building_id=must_be_int(building.id),
            building=building,
            user_id=must_be_int(admin_user.id),
            user=admin_user,
            reservation=reservation,
        )
        session.add(solicitation)
        session.commit()
        reservation_id = must_be_int(reservation.id)

        ReservationRepository.delete(id=reservation_id, user=admin_user, session=session)
        session.commit()

        still_there = ReservationRepository.get_by_id(
            id=reservation_id, session=session
        )
        assert still_there.status == ReservationStatus.DELETED
        assert still_there.solicitation is not None
        assert still_there.solicitation.deleted_by == admin_user.name

    def test_raises_when_the_solicitation_is_already_deleted(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        reservation = _create_reservation(
            admin_user=admin_user, classroom=classroom, session=session
        )
        reservation.status = ReservationStatus.DELETED
        solicitation = Solicitation(
            capacity=10,
            building_id=must_be_int(building.id),
            building=building,
            user_id=must_be_int(admin_user.id),
            user=admin_user,
            reservation=reservation,
        )
        session.add(solicitation)
        session.commit()
        reservation_id = must_be_int(reservation.id)

        with pytest.raises(ReservationAlreadyDeleted):
            ReservationRepository.delete(
                id=reservation_id, user=admin_user, session=session
            )


class TestUpdateOccurrences:
    def test_raises_when_reservation_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ReservationNotFound):
            ReservationRepository.update_occurrences(
                id=999999,
                input=ScheduleUpdateOccurrences(dates=[]),
                session=session,
            )
