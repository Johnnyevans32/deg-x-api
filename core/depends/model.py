from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, ConfigDict

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
    deletedAt: Optional[datetime] = None


class SBaseOutModel(HashableBaseModel, BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: lambda oid: str(oid),
        },
    )


class SBaseModel(SBaseInModel, SBaseOutModel):
    pass
