from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from core.depends.get_object_id import PyObjectId


class HashableBaseModel(BaseModel):
    def __hash__(self) -> int:
        return hash(
            (type(self),)
            + tuple(
                frozenset(getattr(self, f))
                if isinstance(getattr(self, f), dict)
                else getattr(self, f)
                for f in self.__fields__.keys()
            )
        )


class SBaseInModel(HashableBaseModel):
    isDeleted: bool = Field(default=False)
    deletedAt: Optional[datetime] = Field(default=None)


class SBaseOutModel(HashableBaseModel, BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())

    # def __init__(self, **pydict: dict[str, Any]) -> None:
    #     try:
    #         super().__init__(**pydict)
    #         self.id = cast(PyObjectId, pydict.pop("_id"))
    #     except Exception as e:
    #         logger.error(f"Error while mapping the id to record - {e}")

    class Config:
        arbitrary_types_allowed = True


class SBaseModel(SBaseInModel, SBaseOutModel):
    pass
