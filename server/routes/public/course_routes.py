from fastapi import APIRouter, Body

from server.models.http.responses.course_response_models import CourseResponse

from server.deps.session_dep import SessionDep
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
