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

    class Config:
        arbitrary_types_allowed = True


class SBaseModel(SBaseInModel, SBaseOutModel):
    pass
