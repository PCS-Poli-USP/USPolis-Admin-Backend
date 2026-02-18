from fastapi import APIRouter, Body

from server.models.http.responses.course_response_models import CourseResponse

from server.deps.session_dep import SessionDep
from server.repositories.course_repository import CourseRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("")
async def get_all_courses(session: SessionDep) -> list[CourseResponse]:
    """Get all courses"""
    courses = CourseRepository.get_all(session=session)
    return CourseResponse.from_course_list(courses)
