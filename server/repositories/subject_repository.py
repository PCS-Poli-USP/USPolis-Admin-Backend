from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.deps.authenticate import BuildingDep
from server.deps.interval_dep import QueryInterval
from server.models.database.class_db_model import Class
from server.models.database.subject_building_link import SubjectBuildingLink
from server.models.database.subject_db_model import Subject
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from server.models.http.responses.subject_response_models import SubjectCrawlResponse
from server.repositories.building_repository import BuildingRepository
from server.repositories.calendar_repository import CalendarRepository
from server.services.janus_crawler.crawler import JanusCrawler
from server.services.jupiter_crawler.crawler import JupiterCrawler
from server.utils.enums.crawler_type_enum import CrawlerType
from server.utils.enums.subject_type import SubjectType
from server.utils.must_be_int import must_be_int


class SubjectRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Subject]:
        statement = select(Subject).where(col(Subject.id) > 0)
        subjects = session.exec(statement).all()
        return list(subjects)

    @staticmethod
    def get_all_on_interval(
        *, interval: QueryInterval, session: Session
    ) -> list[Subject]:
        statement = select(Subject).join(
            Class, col(Class.subject_id) == col(Subject.id)
        )
        if interval.today:
            statement = statement.where(
                col(Class.end_date) >= interval.today
            ).distinct()

        if interval.start and interval.end:
            statement = statement.where(
                col(Class.start_date) >= interval.start,
                col(Class.end_date) <= interval.end,
            ).distinct()
        subjects = session.exec(statement).all()
        return list(subjects)

    @staticmethod
    def get_all_on_buildings(
        *, building_ids: list[int], session: Session
    ) -> list[Subject]:
        statement = (
            select(Subject)
            .join(SubjectBuildingLink)
            .where(col(SubjectBuildingLink.building_id).in_(building_ids))
            .distinct()
        )
        subjects = session.exec(statement).all()
        return list(subjects)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Subject:
        statement = select(Subject).where(col(Subject.id) == id)
        try:
            subject = session.exec(statement).one()
            return subject
        except NoResultFound:
            raise SubjectNotFound()

    @staticmethod
    def get_by_id_on_buildings(
        *, id: int, building_ids: list[int], session: Session
    ) -> Subject:
        statement = (
            select(Subject)
            .join(SubjectBuildingLink)
            .where(col(SubjectBuildingLink.building_id).in_(building_ids))
            .where(col(Subject.id) == id)
        )
        try:
            subject = session.exec(statement).one()
            return subject
        except NoResultFound:
            raise SubjectNotFound()

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[Subject]:
        statement = select(Subject).where(col(Subject.id).in_(ids))
        subjects = session.exec(statement).all()
        return list(subjects)

    @staticmethod
    def get_by_code(*, code: str, session: Session) -> Subject:
        statement = select(Subject).where(Subject.code == code)
        try:
            subject = session.exec(statement).one()
            return subject
        except NoResultFound:
            raise SubjectNotFound()

    @staticmethod
    def create(*, input: SubjectRegister, session: Session) -> Subject:
        new_subject = Subject(
            buildings=BuildingRepository.get_by_ids(
                ids=input.building_ids, session=session
            ),
            name=input.name,
            code=input.code,
            professors=input.professors,
            type=input.type,
            class_credit=input.class_credit,
            work_credit=input.work_credit,
        )
        session.add(new_subject)
        return new_subject

    @staticmethod
    def __update_crawled_subject_core_data(
        old: Subject, new: Subject, session: Session
    ) -> None:
        old.name = new.name
        old.professors = new.professors
        old.type = new.type
        old.class_credit = new.class_credit
        old.work_credit = new.work_credit

    @staticmethod
    def __update_crawled_subject_class_data(
        old: Subject, crawled: Subject, session: Session
    ) -> None:
        for i in range(len(old.classes)):
            SubjectRepository.__update_crawled_class_core_data(
                old.classes[i], crawled.classes[i], session
            )

    @staticmethod
    def update_crawled_subject_data(
        old: Subject, crawled: Subject, session: Session
    ) -> None:
        SubjectRepository.__update_crawled_subject_core_data(old, crawled, session)
        SubjectRepository.__update_crawled_subject_class_data(old, crawled, session)

    @staticmethod
    async def crawler_create_many(
        subjects_codes: list[str],
        calendar_ids: list[int],
        session: Session,
        building: BuildingDep,
        type: CrawlerType,
    ) -> SubjectCrawlResponse:
        calendars = CalendarRepository.get_by_ids(ids=calendar_ids, session=session)
        errors: list[str] = []
        sucess: list[str] = []
        failed: list[str] = []
        for subject_code in subjects_codes:
            try:
                old = SubjectRepository.get_by_code(code=subject_code, session=session)
            except SubjectNotFound:
                old = None

            try:
                if type == CrawlerType.JUPITER:
                    subject = await JupiterCrawler.crawl_subject_static(
                        subject_code, calendars
                    )
                else:
                    subject = await JanusCrawler.crawl_subject_static(
                        subject_code, calendars
                    )

            except Exception as e:  # noqa: E722
                print(e)
                errors.append(
                    f"Falha ao obter informações da disciplina {subject_code}"
                )
                failed.append(subject_code)
                continue

            new_classes_set = set()
            old_set = set()
            has_add_to_building = False
            if old is not None:
                old_set = set([class_.code for class_ in old.classes])
                crawled_set = set([class_.code for class_ in subject.classes])
                new_classes_set = crawled_set - old_set
                new_classes = [
                    class_
                    for class_ in subject.classes
                    if class_.code in new_classes_set
                ]
                for class_ in new_classes:
                    class_.subject_id = must_be_int(old.id)
                    class_.subject = old
                    session.add(class_)

                SubjectRepository.__update_crawled_subject_core_data(
                    old, subject, session
                )
                if building not in old.buildings:
                    has_add_to_building = True
                    old.buildings.append(building)
                session.add(old)
            else:
                subject.buildings = [building]
                session.add(subject)

            try:
                session.commit()
                if old is not None:
                    if len(old_set) == 0:
                        sucess.append(
                            f"{subject_code} - {len(new_classes_set)} turmas cadastradas"
                        )
                    if has_add_to_building:
                        sucess.append(
                            f"{subject_code} - adicionado ao prédio {building.name}"
                        )
                    if len(old_set) > 0:
                        sucess.append(
                            f"{subject_code} - {len(new_classes_set)} novas turmas cadastradas pelo prédio {building.name} e {len(old_set)} turmas já cadastradas"
                        )
                else:
                    sucess.append(
                        f"{subject_code} - {len(subject.classes)} turmas cadastradas"
                    )

            except Exception as e:  # noqa: E722
                print(e)
                session.reset()
                errors.append(
                    f"Erro ao salvar informações da disciplina {subject_code}"
                )
                failed.append(subject_code)

        return SubjectCrawlResponse(
            codes=subjects_codes, sucess=sucess, failed=failed, errors=errors
        )

    @staticmethod
    def __update_crawled_class_core_data(
        class_: Class, crawled: Class, session: Session
    ) -> None:
        class_.code = crawled.code
        class_.professors = crawled.professors
        class_.type = crawled.type
        class_.vacancies = crawled.vacancies
        class_.updated_at = crawled.updated_at
        session.add(class_)

    @staticmethod
    async def crawler_update_many(
        subject_codes: list[str], session: Session
    ) -> SubjectCrawlResponse:
        errors: list[str] = []
        sucess: list[str] = []
        failed: list[str] = []
        for subject_code in subject_codes:
            try:
                subject = SubjectRepository.get_by_code(
                    code=subject_code, session=session
                )
            except SubjectNotFound:
                errors.append(f"Disciplina {subject_code} não encontrada")
                failed.append(subject_code)
                continue

            try:
                updated = await JupiterCrawler.crawl_subject_static(subject_code)
            except Exception as e:  # noqa: E722
                print(e)
                session.reset()
                errors.append(f"Erro ao obter informações da disciplina {subject_code}")
                failed.append(subject_code)
                continue

            if len(subject.classes) != len(updated.classes):
                errors.append(
                    f"Quantidade de turmas no jupiterWeb é diferente para disciplina {subject_code}"
                )
                failed.append(subject_code)
                continue

            subject.classes.sort(key=lambda x: x.code)
            updated.classes.sort(key=lambda x: x.code)
            for i in range(len(subject.classes)):
                SubjectRepository.__update_crawled_class_core_data(
                    subject.classes[i], updated.classes[i], session
                )
            SubjectRepository.update_crawled_subject_data(subject, updated, session)

            try:
                session.commit()
                sucess.append(subject_code)
            except Exception as e:  # noqa: E722
                print(e)
                session.reset()
                errors.append(
                    f"Erro ao salvar informações da disciplina {subject_code}"
                )
                failed.append(subject_code)

        return SubjectCrawlResponse(
            codes=subject_codes,
            sucess=sucess,
            failed=failed,
            errors=errors,
            update=True,
        )

    @staticmethod
    def __update_subject_core_data(subject: Subject, input: SubjectUpdate) -> None:
        subject.name = input.name
        subject.code = input.code
        subject.professors = input.professors
        subject.type = input.type
        subject.class_credit = input.class_credit
        subject.work_credit = input.work_credit

    @staticmethod
    def update(*, id: int, input: SubjectUpdate, session: Session) -> Subject:
        subject = SubjectRepository.get_by_id(id=id, session=session)
        subject.buildings = BuildingRepository.get_by_ids(
            ids=input.building_ids, session=session
        )
        SubjectRepository.__update_subject_core_data(subject=subject, input=input)
        session.add(subject)
        return subject

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        subject = SubjectRepository.get_by_id(id=id, session=session)
        session.delete(subject)

    @staticmethod
    def create_general_forum(*, id: int, name: str, session: Session) -> Subject:
        new_subject = Subject(
            id=id,
            name=name,
            code="",
            professors=[],
            type=SubjectType.OTHER,
            work_credit=0,
            class_credit=0,
        )
        session.add(new_subject)
        session.commit()
        session.refresh(new_subject)
        return new_subject

    @staticmethod
    def get_by_name(*, name: str, session: Session) -> Subject:
        statement = select(Subject).where(Subject.name == name)
        try:
            subject = session.exec(statement).one()
            return subject
        except NoResultFound:
            raise SubjectNotFound()


class SubjectNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, "Disciplina não encontrada")


class SubjectNotExists(HTTPException):
    def __init__(self, subject_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Disciplina {subject_info} não existe"
        )


class SubjectCreationError(HTTPException):
    def __init__(self, subjects: list, errors: list[str]) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            detail={
                "subjects": subjects,
                "errors": errors,
                "message": f"Erro ao criar as seguintes disciplinas: {', '.join(subjects)}",
            },
        )
