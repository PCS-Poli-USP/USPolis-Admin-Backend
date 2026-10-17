from datetime import date
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Query, status
from pydantic import BaseModel, model_validator

from server.utils.brazil_datetime import BrazilDatetime


class QueryInterval(BaseModel):
    """If start and end date are not given, it will consider everything active today. (everything that already started but not ended)"""

    today: date | None = None
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if not self.today and not self.start and not self.end:
            self.today = BrazilDatetime.now_utc().date()
            return self

        if self.today and (self.start or self.end):
            raise InvalidQueryInterval(
                detail="Erro ao realizar a consulta: não é possível usar o filtro de datas 'Hoje' os filtros 'Início' ou 'Fim'."
            )
        if (self.start and not self.end) or (self.end and not self.start):
            raise InvalidQueryInterval(
                detail="Erro ao realizar a consulta: para usar o filtro de datas por intervalo, tanto 'Início' como 'Fim' devem ser passados."
            )
        if self.start and self.end:
            ensure_valid_span(self.start, self.end, max_days=MAX_INTERVAL_DAYS)

        return self


# Bounds the cost of a single request (an unbounded range is the cheapest DoS).
# One year covers every legitimate use seen in production: semester views of
# classes/reservations by building ask for up to ~365 days.
MAX_INTERVAL_DAYS = 366


def ensure_valid_span(start: date, end: date, *, max_days: int) -> None:
    """Raise InvalidQueryInterval unless start <= end and the interval, counting
    both ends, spans at most `max_days` days."""
    if end < start:
        raise InvalidQueryInterval(
            detail="Erro ao realizar a consulta: a data de fim deve ser igual ou posterior à de início."
        )
    if (end - start).days + 1 > max_days:
        raise InvalidQueryInterval(
            detail=f"Erro ao realizar a consulta: o intervalo de datas pode ter no máximo {max_days} dias."
        )


class InvalidQueryInterval(HTTPException):
    """Exception raised when the query interval is invalid."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


def query_interval_params(
    today: date | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
) -> QueryInterval:
    return QueryInterval(today=today, start=start, end=end)


QueryIntervalDep = Annotated[QueryInterval, Depends(query_interval_params)]
