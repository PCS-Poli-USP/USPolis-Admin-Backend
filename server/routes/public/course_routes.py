from fastapi import APIRouter, Body

from server.models.database.course_options_db_model import CourseOptions
from server.models.http.responses.course_response_models import CourseResponse

from server.deps.session_dep import SessionDep
from server.repositories.course_options_repository import CourseOptionRepository
from server.repositories.course_repository import CourseRepository
from server.services.jupiter_crawler.active_courses_crawler.crawler import JupiterCoursesCrawler
from server.services.jupiter_crawler.course_models import CourseOption
from server.services.jupiter_crawler.inactive_courses_crawler.crawler import JupiterCoursesOldCrawler

embed = Body(..., embed=True)

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("")
async def get_all_courses(session: SessionDep) -> list[CourseResponse]:
    """Get all courses"""
    courses = CourseRepository.get_all(session=session)
    return CourseResponse.from_course_list(courses)

@router.get("/jupiter/inactive-courses")
async def list_inactive_courses(codcg: int = 3) -> list[CourseOption]:
    crawler = JupiterCoursesOldCrawler(codcg=codcg, tipo="V")
    courses = await crawler.crawl()
    return courses

@router.get("/jupiter/active-courses")
async def list_active_courses(codcg: int = 3) -> list[CourseOption]:
    crawler = JupiterCoursesCrawler(codcg=codcg, tipo="N")
    courses = await crawler.crawl()
    return courses

@router.get("/options")
def list_cached_course_options(session: SessionDep) -> list[CourseOption]:
    repo = CourseOptionRepository(session)
    options = repo.list_all()

    return [
        CourseOption(codcur=o.codcur, codhab=o.codhab, name=o.name)
        for o in options
    ]

@router.post("/options/sync")
async def sync_course_options(session: SessionDep, codcg: int = 3) -> list[CourseOption]:
    active = await JupiterCoursesCrawler(codcg=codcg, tipo="N").crawl()
    inactive = await JupiterCoursesOldCrawler(codcg=codcg, tipo="V").crawl()

    all_courses = active + inactive

    repo = CourseOptionRepository(session)

    db_models = [
        CourseOptions(codcur=c.codcur, codhab=c.codhab, name=c.name)
        for c in all_courses
    ]

    repo.upsert_many(db_models)

    # retorna o que foi salvo
    saved = repo.list_all()
    return [
        CourseOption(codcur=o.codcur, codhab=o.codhab, name=o.name)
        for o in saved
    ]
