from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from sqlmodel import Session

from server.deps.session_dep import SessionDep
from server.middlewares.request_utils import get_client_ip
from server.models.http.requests.search_request_models import SearchLogRequest
from server.models.http.responses.search_response_models import (
    SearchGroupResponse,
    SearchResponse,
    SearchTopResponse,
)
from server.repositories.search_repository import SearchHit, SearchRepository
from server.services.search_log_service import record_search
from server.utils.enums.search_entity_type import SearchEntityType

router = APIRouter(prefix="/search", tags=["Search"])

RelatedLimit = Annotated[int, Query(ge=0, le=20)]


def _expand(hit: SearchHit, related_limit: int, session: Session) -> SearchTopResponse:
    related = (
        SearchRepository.related(hit=hit, limit_per_type=related_limit, session=session)
        if related_limit > 0
        else []
    )
    return SearchTopResponse.from_hit_and_related(hit, related)


@router.get("")
async def search(
    session: SessionDep,
    q: Annotated[str, Query(min_length=2, max_length=100)],
    types: Annotated[list[SearchEntityType] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
    related_limit: RelatedLimit = 6,
) -> SearchResponse:
    """General public search over subjects, classes, classrooms, buildings
    and professors.

    Returns the best match (`top`) expanded with the documents linked to it
    (`top.related`), and the best `limit` results of each type (`groups`),
    best group first. The index is a materialized view refreshed every few
    minutes, so very recent changes may take a moment to show up."""
    hits = SearchRepository.search(
        query=q,
        types=types or SearchEntityType.values(),
        limit_per_type=limit,
        session=session,
    )
    top = _expand(hits[0], related_limit, session) if hits else None
    return SearchResponse(query=q, top=top, groups=SearchGroupResponse.from_hits(hits))


@router.post("/log", status_code=status.HTTP_204_NO_CONTENT)
async def log_search(
    request: Request, session: SessionDep, body: SearchLogRequest
) -> None:
    """Record a search the user settled on, for finding what people look for
    and do not find (see docs/SEARCH.md, "Query log").

    The client calls this once per query, after the user stops typing or
    opens a result, not on every keystroke. The record is anonymous and
    aggregated per day: the normalized query, the type filter, how many times
    it was searched and how many results it had (recomputed here, never
    trusted from the client). Always answers 204: queries that look like
    personal data, and new queries past the per-IP or daily caps, are
    accepted but not recorded."""
    await record_search(
        query=body.q,
        types=body.types,
        host=get_client_ip(request),
        session=session,
    )


@router.get("/documents/{doc_key}")
async def get_search_document(
    session: SessionDep,
    doc_key: Annotated[str, Path(max_length=200, examples=["subject:12"])],
    related_limit: RelatedLimit = 6,
) -> SearchTopResponse:
    """One search document (by `doc_key`, e.g. `classroom:5`) expanded with its
    related documents. Lets the client move from a result to the entities
    linked to it without a new text search."""
    hit = SearchRepository.get_by_doc_key(doc_key=doc_key, session=session)
    if hit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento de busca não encontrado",
        )
    return _expand(hit, related_limit, session)
