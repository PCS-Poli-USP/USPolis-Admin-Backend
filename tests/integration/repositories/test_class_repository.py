from datetime import date, timedelta

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.class_repository import ClassNotFound, ClassRepository
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.schedule_permission_checker import (
    ForbiddenScheduleAccess,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.calendar_model_factory import CalendarModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.request.class_request_factory import ClassRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


class TestGetAll:
    def test_returns_classes_active_today_by_default(
        self, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all(session=session, interval=QueryInterval())

        assert class_.id in [c.id for c in classes]

    def test_excludes_classes_outside_the_start_end_interval(
        self, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all(
            session=session,
            interval=QueryInterval(start=date(1999, 1, 1), end=date(1999, 12, 31)),
        )

        assert class_.id not in [c.id for c in classes]


class TestGetAllAllocatedOnBuilding:
    def test_returns_classes_allocated_in_the_given_building(
        self,
        allocated_classroom: Classroom,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        classes = ClassRepository.get_all_allocated_on_building(
            building_id=must_be_int(building.id),
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id in [c.id for c in classes]

    def test_excludes_unallocated_classes(
        self, building: Building, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_allocated_on_building(
            building_id=must_be_int(building.id),
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id not in [c.id for c in classes]


class TestGetAllUnallocatedOnBuildings:
    def test_returns_unallocated_classes_of_the_given_buildings(
        self, building: Building, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_unallocated_on_buildings(
            building_ids=[must_be_int(building.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id in [c.id for c in classes]

    def test_excludes_allocated_classes(
        self,
        allocated_classroom: Classroom,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        classes = ClassRepository.get_all_unallocated_on_buildings(
            building_ids=[must_be_int(building.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id not in [c.id for c in classes]


class TestGetAllOnClassrooms:
    def test_returns_classes_scheduled_in_the_given_classroom(
        self,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        classes = ClassRepository.get_all_on_classrooms(
            classroom_ids=[must_be_int(allocated_classroom.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id in [c.id for c in classes]

    def test_excludes_classes_of_other_classrooms(
        self, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_on_classrooms(
            classroom_ids=[999999], session=session, interval=QueryInterval()
        )

        assert class_.id not in [c.id for c in classes]


class TestGetAllOnBuildings:
    def test_returns_classes_of_subjects_in_the_given_building(
        self, building: Building, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_on_buildings(
            building_ids=[must_be_int(building.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id in [c.id for c in classes]

    def test_excludes_classes_of_other_buildings(
        self, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_on_buildings(
            building_ids=[999999], session=session, interval=QueryInterval()
        )

        assert class_.id not in [c.id for c in classes]


class TestGetAllOnSubject:
    def test_returns_classes_of_the_given_subject(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_on_subject(
            subject_id=must_be_int(subject.id),
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id in [c.id for c in classes]

    def test_returns_empty_for_a_subject_with_no_classes(
        self, building: Building, session: Session
    ) -> None:
        other_subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()

        classes = ClassRepository.get_all_on_subject(
            subject_id=must_be_int(other_subject.id),
            session=session,
            interval=QueryInterval(),
        )

        assert classes == []


class TestGetAllAllocatedBySubjects:
    def test_excludes_subjects_with_an_unallocated_schedule(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        classes = ClassRepository.get_all_allocated_by_subjects(
            subject_ids=[must_be_int(subject.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id not in [c.id for c in classes]

    def test_returns_classes_whose_schedules_are_all_allocated(
        self,
        subject: Subject,
        class_: Class,
        allocated_classroom: Classroom,
        session: Session,
    ) -> None:
        classes = ClassRepository.get_all_allocated_by_subjects(
            subject_ids=[must_be_int(subject.id)],
            session=session,
            interval=QueryInterval(),
        )

        assert class_.id in [c.id for c in classes]


class TestGetById:
    def test_returns_the_matching_class(
        self, class_: Class, session: Session
    ) -> None:
        found = ClassRepository.get_by_id(id=must_be_int(class_.id), session=session)

        assert found.id == class_.id

    def test_raises_when_class_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ClassNotFound):
            ClassRepository.get_by_id(id=999999, session=session)


class TestGetByIds:
    def test_returns_only_the_matching_classes(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        other_class = ClassModelFactory(
            subject=subject, session=session
        ).create_and_refresh()

        found = ClassRepository.get_by_ids(
            ids=[must_be_int(class_.id), must_be_int(other_class.id)], session=session
        )

        assert {c.id for c in found} == {class_.id, other_class.id}


class TestGetByIdOnBuilding:
    def test_returns_the_class_when_its_subject_belongs_to_the_building(
        self, building: Building, class_: Class, session: Session
    ) -> None:
        found = ClassRepository.get_by_id_on_building(
            id=must_be_int(class_.id), building=building, session=session
        )

        assert found.id == class_.id

    def test_raises_when_the_building_does_not_match(
        self, admin_user: User, class_: Class, session: Session
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()

        with pytest.raises(ClassNotFound):
            ClassRepository.get_by_id_on_building(
                id=must_be_int(class_.id), building=other_building, session=session
            )


class TestGetByIdOnBuildings:
    def test_returns_the_class_when_its_building_matches(
        self, building: Building, class_: Class, session: Session
    ) -> None:
        found = ClassRepository.get_by_id_on_buildings(
            id=must_be_int(class_.id),
            building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert found.id == class_.id

    def test_raises_when_the_building_does_not_match(
        self, class_: Class, session: Session
    ) -> None:
        with pytest.raises(ClassNotFound):
            ClassRepository.get_by_id_on_buildings(
                id=must_be_int(class_.id), building_ids=[999999], session=session
            )


class TestGetBySubjectCodeAndClassCode:
    def test_returns_the_matching_class(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        found = ClassRepository.get_by_subject_code_and_class_code(
            subject_code=subject.code, class_code=class_.code, session=session
        )

        assert found.id == class_.id

    def test_raises_when_the_pair_does_not_match(
        self, subject: Subject, session: Session
    ) -> None:
        with pytest.raises(ClassNotFound):
            ClassRepository.get_by_subject_code_and_class_code(
                subject_code=subject.code, class_code="DOES-NOT-EXIST", session=session
            )


class TestGetBySubjectCodesAndClassCodes:
    def test_returns_only_the_matching_pairs(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        found = ClassRepository.get_by_subject_codes_and_class_codes(
            pairs=[(subject.code, class_.code)], session=session
        )

        assert [c.id for c in found] == [class_.id]

    def test_returns_empty_for_an_empty_list_of_pairs(self, session: Session) -> None:
        assert ClassRepository.get_by_subject_codes_and_class_codes(
            pairs=[], session=session
        ) == []


class TestGetComming:
    def test_returns_classes_with_an_occurrence_in_the_next_two_days(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        OccurrenceModelFactory(schedule=schedule, session=session).create_and_refresh(
            date=BrazilDatetime.now_utc().date() + timedelta(days=1)
        )

        classes = ClassRepository.get_comming(session=session)

        assert class_.id in [c.id for c in classes]


class TestCreate:
    def test_creates_a_class_with_its_schedules(
        self, subject: Subject, session: Session
    ) -> None:
        input = ClassRequestFactory(subject=subject).create_input()

        class_ = ClassRepository.create(input=input, session=session)
        session.commit()
        session.refresh(class_)

        assert class_.code == input.code
        assert class_.subject_id == subject.id
        assert len(class_.schedules) == 1
        assert class_.calendars == []

    def test_creates_a_class_with_calendars(
        self, admin_user: User, subject: Subject, session: Session
    ) -> None:
        calendar = CalendarModelFactory(
            creator=admin_user, session=session
        ).create_and_refresh()
        input = ClassRequestFactory(subject=subject).create_input(
            calendar_ids=[must_be_int(calendar.id)]
        )

        class_ = ClassRepository.create(input=input, session=session)
        session.commit()
        session.refresh(class_)

        assert [c.id for c in class_.calendars] == [calendar.id]


class TestUpdate:
    def test_updates_core_fields_and_subject(
        self, admin_user: User, subject: Subject, class_: Class, session: Session
    ) -> None:
        other_subject = SubjectModelFactory(
            building=subject.buildings[0], session=session
        ).create_and_refresh()
        update_input = ClassRequestFactory(subject=other_subject).update_input(
            code="NEWCODE"
        )

        updated = ClassRepository.update(
            id=must_be_int(class_.id),
            input=update_input,
            user=admin_user,
            session=session,
            permission_index=build_permission_index(admin_user),
        )
        session.commit()
        session.refresh(updated)

        assert updated.code == "NEWCODE"
        assert updated.subject_id == other_subject.id

    def test_raises_when_class_does_not_exist(
        self, admin_user: User, subject: Subject, session: Session
    ) -> None:
        update_input = ClassRequestFactory(subject=subject).update_input()

        with pytest.raises(ClassNotFound):
            ClassRepository.update(
                id=999999,
                input=update_input,
                user=admin_user,
                session=session,
                permission_index=build_permission_index(admin_user),
            )

    def test_adding_a_calendar_requires_schedule_permission(
        self,
        admin_user: User,
        common_user: User,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        calendar = CalendarModelFactory(
            creator=admin_user, session=session
        ).create_and_refresh()
        update_input = ClassRequestFactory(subject=subject).update_input(
            calendar_ids=[must_be_int(calendar.id)]
        )

        with pytest.raises(ForbiddenScheduleAccess):
            ClassRepository.update(
                id=must_be_int(class_.id),
                input=update_input,
                user=common_user,
                session=session,
                permission_index=build_permission_index(common_user),
            )

    def test_adding_a_calendar_succeeds_with_schedule_permission(
        self,
        admin_user: User,
        common_user: User,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        calendar = CalendarModelFactory(
            creator=admin_user, session=session
        ).create_and_refresh()
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(subject.buildings[0].id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        update_input = ClassRequestFactory(subject=subject).update_input(
            calendar_ids=[must_be_int(calendar.id)]
        )

        updated = ClassRepository.update(
            id=must_be_int(class_.id),
            input=update_input,
            user=common_user,
            session=session,
            permission_index=build_permission_index(common_user),
        )
        session.commit()
        session.refresh(updated)

        assert [c.id for c in updated.calendars] == [calendar.id]


class TestDelete:
    def test_deletes_the_class(self, class_: Class, session: Session) -> None:
        class_id = must_be_int(class_.id)

        ClassRepository.delete(id=class_id, session=session)
        session.commit()

        with pytest.raises(ClassNotFound):
            ClassRepository.get_by_id(id=class_id, session=session)

    def test_raises_when_class_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ClassNotFound):
            ClassRepository.delete(id=999999, session=session)


class TestDeleteMany:
    def test_deletes_every_given_class(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        other_class = ClassModelFactory(
            subject=subject, session=session
        ).create_and_refresh()
        ids = [must_be_int(class_.id), must_be_int(other_class.id)]

        ClassRepository.delete_many(ids=ids, session=session)
        session.commit()

        assert ClassRepository.get_by_ids(ids=ids, session=session) == []
