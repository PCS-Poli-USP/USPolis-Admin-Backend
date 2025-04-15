from typing import TypedDict


class BuildingRegisterDict(TypedDict, total=False):
    name: str


class BuildingUpdateDict(BuildingRegisterDict, total=False):
    pass
