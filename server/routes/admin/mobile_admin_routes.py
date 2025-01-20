from dotenv import load_dotenv
from fastapi import APIRouter


from server.deps.session_dep import SessionDep
from server.models.database.mobile_user_db_model import MobileUser
from server.models.database.subject_db_model import Subject
from server.models.http.requests.forum_request_models import ForumPostRegister
from server.models.http.responses.forum_post_response import ForumPostResponse
from server.repositories.mobile_user_repository import MobileUserRepository
from server.models.http.responses.mobile_auth_user_response_models import (
    AuthenticationResponse,
)
from server.repositories.subject_repository import SubjectNotFound, SubjectRepository
from server.models.http.requests.forum_request_models import (
    to_forumpost_model,
)
from server.repositories.forum_repository import ForumRepository

router = APIRouter(prefix="/mobile/authentication", tags=["Mobile", "Authenticate"])

# Carregar variáveis do arquivo .env
load_dotenv()


@router.post("/new-mock-user")
async def create_new_user(session: SessionDep) -> AuthenticationResponse:
    newUser = MobileUser(
        sub="mock",
        given_name="mock",
        family_name="mock",
        email="mock",
        picture_url="mock",
    )

    new_user = MobileUserRepository.create(new_user=newUser, session=session)
    return AuthenticationResponse.from_model_user(new_user)


@router.post("/mock-posts")
async def create_forum_post(
    input: ForumPostRegister,
    session: SessionDep,
) -> ForumPostResponse:
    """Create a forum post with provided tags. The General Forum is associeted with subject_id == -1"""
    if input.subject_id == -1:
        globalForumSubject: Subject
        try:
            globalForumSubject = SubjectRepository.get_by_name(
                name="Forum Geral", session=session
            )
        except SubjectNotFound:
            globalForumSubject = SubjectRepository.create_general_forum(
                id=input.subject_id, name="Forum Geral", session=session
            )

        input.subject_id = globalForumSubject.id  # type: ignore
        input.class_id = None

    forum_post = ForumRepository.create(
        input=to_forumpost_model(input), session=session
    )

    return ForumPostResponse.from_forum_post(input.user_id, forum_post, session)
