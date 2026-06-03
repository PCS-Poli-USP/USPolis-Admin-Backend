from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from server.deps.authenticate import UserDep
from server.deps.session_dep import SessionDep
from server.models.http.requests.jupiter_request_models import JupiterLoginRequest
from server.models.http.requests.user_schedule_request_models import (
    UserScheduleRegister,
    UserScheduleUpdate,
)
from server.models.http.responses.user_schedule_response import (
    UserScheduleCrawlResponse,
    UserScheduleResponse,
)
from server.repositories.class_repository import ClassRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.repositories.subject_repository import SubjectRepository
from server.repositories.user_schedule_repository import UserScheduleRepository
from server.services.jupiter_crawler.authenticated_crawler import (
    AuthenticatedJupiterCrawler,
    JupiterAuthenticationError,
)
from server.services.jupiter_crawler.models import JupiterStudentSubject
from server.utils.enums.crawler_enums import CrawlerStatus
from server.utils.must_be_int import must_be_int


router = APIRouter(prefix="/users/schedules", tags=["UserSchedules"])


@router.post("/crawl")
async def crawl_user_schedule(
    input: JupiterLoginRequest, user: UserDep, session: SessionDep
) -> UserScheduleCrawlResponse:
    """Crawl the schedule for the authenticated user"""
    try:
        try:
            jupiter_schedule = (
                await AuthenticatedJupiterCrawler.crawl_student_schedule_static(
                    n_usp=input.n_usp,
                    password=input.password,
                )
            )
        except JupiterAuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao acessar o JupiterWeb: {str(exc)}",
            ) from exc

        pairs = [(data.code, data.class_code) for data in jupiter_schedule.subjects]
        subject_codes = [p[0] for p in pairs]
        subjects = SubjectRepository.get_by_codes(codes=subject_codes, session=session)

        existing_subject_codes = {s.code for s in subjects}
        missing_subject_codes = set(subject_codes) - existing_subject_codes
        missing_items: list[JupiterStudentSubject] = []
        if missing_subject_codes:
            for sub in jupiter_schedule.subjects:
                if sub.code in missing_subject_codes:
                    missing_items.append(sub)

        classes = ClassRepository.get_by_subject_codes_and_class_codes(
            pairs=pairs, session=session
        )
        schedules = [s for c in classes for s in c.schedules]
        start_date = min((s.start_date for s in schedules), default=None)
        end_date = max((s.end_date for s in schedules), default=None)
        crawl_succeeded = start_date is not None and end_date is not None
        updated = False

        old_user_schedule, _ = UserScheduleRepository.get_active_current_schedule(
            user=user, session=session
        )

        message = "Grade horária obtida com sucesso."
        user_schedule = old_user_schedule
        if crawl_succeeded:
            if old_user_schedule:
                crawled_schedule_ids = {
                    must_be_int(schedule.id) for schedule in schedules
                }
                current_schedule_ids = {
                    must_be_int(entry.schedule_id)
                    for entry in old_user_schedule.entries
                }
                should_update_schedule = (
                    old_user_schedule.start_date != start_date
                    or old_user_schedule.end_date != end_date
                    or current_schedule_ids != crawled_schedule_ids
                )
                if should_update_schedule:
                    user_schedule = UserScheduleRepository.update_from_schedules(
                        user_schedule=old_user_schedule,
                        schedules=schedules,
                        session=session,
                    )
                    updated = True
                    message = "Grade horária atualizada com sucesso."
                else:
                    message = "Grade horária obtida, mas nenhuma mudança foi detectada."

            else:
                user_schedule = UserScheduleRepository.create_from_schedules(
                    user=user, schedules=schedules, session=session
                )
                message = "Grade horária criada com sucesso."

        user.current_schedule = user_schedule
        try:
            session.commit()
        except Exception as exc:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar a grade horária: {str(exc)}",
            ) from exc

        crawl_status = (
            CrawlerStatus.SUCCESS
            if crawl_succeeded and not missing_subject_codes
            else CrawlerStatus.WARNING
            if crawl_succeeded
            else CrawlerStatus.FAILURE
        )

        if crawl_status == CrawlerStatus.WARNING:
            message += (
                " No entanto, os seguintes códigos de disciplina não foram encontrados no sistema: "
                + ", ".join(missing_subject_codes)
            )

        return UserScheduleCrawlResponse(
            status=crawl_status,
            updated=updated,
            user_schedule=UserScheduleResponse.from_user_schedule(
                user=user, user_schedule=user_schedule
            ),
            user_schedule_crawled=jupiter_schedule,
            missing_items=missing_items,
            message=message,
        )

    except JupiterAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while scraping JupiterWeb: {str(exc)}",
        ) from exc


@router.post("")
def create_user_schedule(
    user: UserDep,
    input: UserScheduleRegister,
    session: SessionDep,
) -> JSONResponse:
    schedules = ScheduleRepository.get_by_ids(ids=input.schedule_ids, session=session)
    user_schedule = UserScheduleRepository.create_from_schedules(
        user=user, schedules=schedules, session=session
    )
    user.current_schedule = user_schedule
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Grade horária criada com sucesso!",
        },
    )


@router.put("/{user_schedule_id}")
def update_user_schedule(
    user_schedule_id: int,
    input: UserScheduleUpdate,
    user: UserDep,
    session: SessionDep,
) -> JSONResponse:
    user_schedule = UserScheduleRepository.get_by_id(
        id=user_schedule_id, session=session
    )
    if not user_schedule:
        raise UserScheduleNotFoundError()

    schedules = ScheduleRepository.get_by_ids(ids=input.schedule_ids, session=session)
    updated = UserScheduleRepository.update_from_schedules(
        user_schedule=user_schedule, schedules=schedules, session=session
    )
    user.current_schedule = updated
    session.add(user)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Grade horária atualizada com sucesso!"},
    )


@router.delete("/{user_schedule_id}")
def delete_user_schedule(
    user_schedule_id: int,
    user: UserDep,
    session: SessionDep,
) -> JSONResponse:
    user_schedule = UserScheduleRepository.get_by_id(
        id=user_schedule_id, session=session
    )
    if not user_schedule:
        raise UserScheduleNotFoundError()

    if user.id != user_schedule.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para excluir esta grade horária",
        )

    UserScheduleRepository.delete(user_schedule, session=session)
    user.current_schedule = None
    session.add(user)
    session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Grade horária excluída com sucesso!"},
    )


class UserScheduleNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade horária do usuário não encontrada",
        )
