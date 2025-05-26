from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)

    def __hash__(self) -> int:
        if hasattr(self, "id") and self.id is not None:
            return hash((type(self), self.id))
        else:
            return hash(id(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        if hasattr(self, "id") and hasattr(other, "id"):
            if self.id is not None and other.id is not None:
                return self.id == other.id
        return id(self) == id(other)
