from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, schema

from core.depends.get_object_id import PyObjectId
from core.utils.loggly import logger


def field_schema(field, **kwargs: Any) -> Any:
    if field.field_info.extra.get("hidden_from_schema", False):
        raise schema.SkipField(f"{field.name} field is being hidden")
    else:
        return original_field_schema(field, **kwargs)


original_field_schema = schema.field_schema
schema.field_schema = field_schema


class SBaseInModel(BaseModel):
    isDeleted: bool = Field(default=False, hidden_from_schema=True)
    deletedAt: datetime = Field(default=None, hidden_from_schema=True)


class SBaseOutModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())

    def __init__(self, **pydict):
        try:
            super().__init__(**pydict)
            self.id = pydict.pop("_id")
        except Exception as e:
            logger.error(f"Error while mapping the id to record - {e}")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: datetime.isoformat, ObjectId: str}
        allow_population_by_field_name = True


class SBaseModel(SBaseInModel, SBaseOutModel):
    pass
