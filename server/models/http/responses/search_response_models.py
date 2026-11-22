from datetime import datetime
from typing import Any

from pydantic import BaseModel

from server.repositories.search_query_log_repository import SearchQueryStat
from server.repositories.search_repository import SearchHit
from server.utils.enums.search_entity_type import SearchEntityType


class SearchItemResponse(BaseModel):
    doc_key: str
    type: SearchEntityType
    entity_id: str
    title: str
    subtitle: str | None
    score: float
    payload: dict[str, Any]

    @classmethod
    def from_hit(cls, hit: SearchHit) -> "SearchItemResponse":
        return cls(
            doc_key=hit.doc_key,
            type=hit.entity_type,
            entity_id=hit.entity_id,
            title=hit.title,
            subtitle=hit.subtitle,
            score=round(hit.score, 4),
            payload=hit.payload,
        )


class SearchGroupResponse(BaseModel):
    type: SearchEntityType
    total: int
    items: list[SearchItemResponse]

    @classmethod
    def from_hits(cls, hits: list[SearchHit]) -> list["SearchGroupResponse"]:
        """Group hits by type, keeping the order in which each type first
        appears (hits come sorted by score, so the best group comes first)."""
        groups: dict[SearchEntityType, SearchGroupResponse] = {}
        for hit in hits:
            group = groups.get(hit.entity_type)
            if group is None:
                group = cls(type=hit.entity_type, total=hit.total, items=[])
                groups[hit.entity_type] = group
            group.items.append(SearchItemResponse.from_hit(hit))
        return list(groups.values())


class SearchTopResponse(SearchItemResponse):
    related: list[SearchGroupResponse]

    @classmethod
    def from_hit_and_related(
        cls, hit: SearchHit, related: list[SearchHit]
    ) -> "SearchTopResponse":
        item = SearchItemResponse.from_hit(hit)
        return cls(**item.model_dump(), related=SearchGroupResponse.from_hits(related))


class SearchResponse(BaseModel):
    query: str
    top: SearchTopResponse | None
    groups: list[SearchGroupResponse]


class SearchQueryStatResponse(BaseModel):
    query: str
    searches: int
    # Searches of this query that returned nothing.
    empty_searches: int
    last_result_count: int
    last_searched_at: datetime

    @classmethod
    def from_stat(cls, stat: SearchQueryStat) -> "SearchQueryStatResponse":
        return cls(
            query=stat.query,
            searches=stat.searches,
            empty_searches=stat.empty_searches,
            last_result_count=stat.last_result_count,
            last_searched_at=stat.last_searched_at,
        )


class SearchLogSummaryResponse(BaseModel):
    since_days: int
    total_searches: int
    distinct_queries: int
    empty_searches: int
    queries: list[SearchQueryStatResponse]
