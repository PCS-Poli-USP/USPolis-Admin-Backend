from datetime import date
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Query, status
from pydantic import BaseModel, model_validator

from server.utils.brazil_datetime import BrazilDatetime


class QueryInterval(BaseModel):
    today: date | None = None
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if not self.today and not self.start and not self.end:
            current_semester = BrazilDatetime.current_semester()
            self.start = current_semester[0]
            self.end = current_semester[1]
            return self

        if self.today and (self.start or self.end):
            raise InvalidQueryInterval(
                detail="Erro ao realizar a consulta: não é possível usar o filtro de datas 'Hoje' os filtros 'Início' ou 'Fim'."
            )
        if (self.start and not self.end) or (self.end and not self.start):
            raise InvalidQueryInterval(
                detail="Erro ao realizar a consulta: para usar o filtro de datas por intervalo, tanto 'Início' como 'Fim' devem ser passados."
            )

        return self


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
