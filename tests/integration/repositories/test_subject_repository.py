from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.subject_repository import SubjectNotFound, SubjectRepository
from server.utils.enums.crawler_enums import CrawlerType
from server.utils.enums.subject_type import SubjectType
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.request.subject_request_factory import SubjectRequestFactory


class TestGetAll:
    def test_excludes_the_sentinel_general_forum_subject(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        SubjectRepository.create_general_forum(
            id=-1, name="Forum Geral", session=session
        )
        session.commit()

        subjects = SubjectRepository.get_all(session=session)

        ids = [s.id for s in subjects]
        assert subject.id in ids
        assert -1 not in ids


class TestGetAllOnInterval:
    def test_returns_subjects_with_an_active_class_by_default(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        ClassModelFactory(subject=subject, session=session).create_and_refresh()

        subjects = SubjectRepository.get_all_on_interval(
            interval=QueryInterval(), session=session
        )

        assert subject.id in [s.id for s in subjects]

    def test_excludes_subjects_outside_the_start_end_interval(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        ClassModelFactory(subject=subject, session=session).create_and_refresh()

        subjects = SubjectRepository.get_all_on_interval(
            interval=QueryInterval(start=date(1999, 1, 1), end=date(1999, 12, 31)),
            session=session,
        )

        assert subject.id not in [s.id for s in subjects]


class TestGetAllOnBuildings:
    def test_returns_subjects_linked_to_the_given_building(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()

        subjects = SubjectRepository.get_all_on_buildings(
            building_ids=[must_be_int(building.id)], session=session
        )

        assert subject.id in [s.id for s in subjects]

    def test_excludes_subjects_of_other_buildings(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()

        subjects = SubjectRepository.get_all_on_buildings(
            building_ids=[999999], session=session
        )

        assert subject.id not in [s.id for s in subjects]


class TestGetById:
    def test_returns_the_matching_subject(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()

        found = SubjectRepository.get_by_id(id=must_be_int(subject.id), session=session)

        assert found.id == subject.id

    def test_raises_when_subject_does_not_exist(self, session: Session) -> None:
        with pytest.raises(SubjectNotFound):
            SubjectRepository.get_by_id(id=999999, session=session)


class TestGetByIdOnBuildings:
    def test_returns_the_subject_when_its_building_matches(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()

        found = SubjectRepository.get_by_id_on_buildings(
            id=must_be_int(subject.id),
            building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert found.id == subject.id

    def test_raises_when_the_building_does_not_match(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()

        with pytest.raises(SubjectNotFound):
            SubjectRepository.get_by_id_on_buildings(
                id=must_be_int(subject.id), building_ids=[999999], session=session
            )


class TestGetByIds:
    def test_returns_only_the_matching_subjects(
        self, building: Building, session: Session
    ) -> None:
        subject1 = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        subject2 = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        SubjectModelFactory(building=building, session=session).create_and_refresh()

        found = SubjectRepository.get_by_ids(
            ids=[must_be_int(subject1.id), must_be_int(subject2.id)], session=session
        )

        assert {s.id for s in found} == {subject1.id, subject2.id}


class TestGetByCode:
    def test_returns_the_matching_subject(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh(code="MAC0110")

        found = SubjectRepository.get_by_code(code="MAC0110", session=session)

        assert found.id == subject.id

    def test_raises_when_subject_does_not_exist(self, session: Session) -> None:
        with pytest.raises(SubjectNotFound):
            SubjectRepository.get_by_code(code="MAC9999", session=session)


class TestGetByCodes:
    def test_returns_only_the_matching_subjects(
        self, building: Building, session: Session
    ) -> None:
        subject1 = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh(code="MAC0110")
        SubjectModelFactory(building=building, session=session).create_and_refresh(
            code="MAC0323"
        )

        found = SubjectRepository.get_by_codes(codes=["MAC0110"], session=session)

        assert [s.id for s in found] == [subject1.id]


class TestGetByName:
    def test_returns_the_matching_subject(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh(name="Introdução à Computação")

        found = SubjectRepository.get_by_name(
            name="Introdução à Computação", session=session
        )

        assert found.id == subject.id

    def test_raises_when_subject_does_not_exist(self, session: Session) -> None:
        with pytest.raises(SubjectNotFound):
            SubjectRepository.get_by_name(name="Does Not Exist", session=session)


class TestCreate:
    def test_creates_a_subject_linked_to_the_given_buildings(
        self, building: Building, session: Session
    ) -> None:
        input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).create_input()

        subject = SubjectRepository.create(input=input, session=session)
        session.commit()
        session.refresh(subject)

        assert subject.code == input.code
        assert subject.name == input.name
        assert [b.id for b in subject.buildings] == [building.id]


class TestUpdate:
    def test_updates_core_data_and_buildings(
        self, admin_user: User, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()

        update_input = SubjectRequestFactory(
            building_ids=[must_be_int(other_building.id)]
        ).update_input(name="Novo Nome", code="MAC0499")

        updated = SubjectRepository.update(
            id=must_be_int(subject.id), input=update_input, session=session
        )
        session.commit()
        session.refresh(updated)

        assert updated.name == "Novo Nome"
        assert updated.code == "MAC0499"
        assert [b.id for b in updated.buildings] == [other_building.id]

    def test_raises_when_subject_does_not_exist(
        self, building: Building, session: Session
    ) -> None:
        update_input = SubjectRequestFactory(
            building_ids=[must_be_int(building.id)]
        ).update_input()

        with pytest.raises(SubjectNotFound):
            SubjectRepository.update(id=999999, input=update_input, session=session)


class TestDelete:
    def test_deletes_the_subject(self, building: Building, session: Session) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh()
        subject_id = must_be_int(subject.id)

        SubjectRepository.delete(id=subject_id, session=session)
        session.commit()

        with pytest.raises(SubjectNotFound):
            SubjectRepository.get_by_id(id=subject_id, session=session)

    def test_raises_when_subject_does_not_exist(self, session: Session) -> None:
        with pytest.raises(SubjectNotFound):
            SubjectRepository.delete(id=999999, session=session)


class TestCreateGeneralForum:
    def test_creates_a_subject_with_the_given_id_and_name(
        self, session: Session
    ) -> None:
        subject = SubjectRepository.create_general_forum(
            id=-1, name="Forum Geral", session=session
        )

        assert subject.id == -1
        assert subject.name == "Forum Geral"
        assert subject.type == SubjectType.OTHER


@pytest.mark.asyncio
class TestCrawlerCreateMany:
    async def test_creates_a_new_subject_from_the_crawler(
        self, building: Building, session: Session
    ) -> None:
        crawled = Subject(
            name="Cálculo I",
            code="MAT0111",
            professors=["Fulano"],
            type=SubjectType.BIANNUAL,
            class_credit=4,
            work_credit=0,
        )
        crawled.classes = []

        with patch(
            "server.repositories.subject_repository.JupiterCrawler.crawl_subject_static",
            new=AsyncMock(return_value=crawled),
        ):
            response = await SubjectRepository.crawler_create_many(
                subjects_codes=["MAT0111"],
                calendar_ids=[],
                session=session,
                building=building,
                type=CrawlerType.JUPITER,
            )

        assert response.failed == []
        assert response.errors == []
        created = SubjectRepository.get_by_code(code="MAT0111", session=session)
        assert created.buildings == [building]

    async def test_records_a_failure_when_the_crawler_raises(
        self, building: Building, session: Session
    ) -> None:
        with patch(
            "server.repositories.subject_repository.JupiterCrawler.crawl_subject_static",
            new=AsyncMock(side_effect=ValueError("boom")),
        ):
            response = await SubjectRepository.crawler_create_many(
                subjects_codes=["MAT0111"],
                calendar_ids=[],
                session=session,
                building=building,
                type=CrawlerType.JUPITER,
            )

        assert response.failed == ["MAT0111"]
        assert response.sucess == []


@pytest.mark.asyncio
class TestCrawlerUpdateMany:
    async def test_records_a_failure_for_an_unknown_subject(
        self, session: Session
    ) -> None:
        response = await SubjectRepository.crawler_update_many(
            subject_codes=["MAT0111"], session=session
        )

        assert response.failed == ["MAT0111"]
        assert "não encontrada" in response.errors[0]

    async def test_records_a_failure_when_class_counts_differ(
        self, building: Building, session: Session
    ) -> None:
        subject = SubjectModelFactory(
            building=building, session=session
        ).create_and_refresh(code="MAT0111")
        ClassModelFactory(subject=subject, session=session).create_and_refresh()

        crawled = Subject(
            name=subject.name,
            code=subject.code,
            professors=subject.professors,
            type=subject.type,
            class_credit=subject.class_credit,
            work_credit=subject.work_credit,
        )
        crawled.classes = []

        with patch(
            "server.repositories.subject_repository.JupiterCrawler.crawl_subject_static",
            new=AsyncMock(return_value=crawled),
        ):
            response = await SubjectRepository.crawler_update_many(
                subject_codes=["MAT0111"], session=session
            )

        assert response.failed == ["MAT0111"]
