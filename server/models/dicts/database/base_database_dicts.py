from typing import TypedDict


class BaseModelDict(TypedDict, total=False):
    id: int | None
