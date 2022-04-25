from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from core.depends.get_object_id import PyObjectId
from core.utils.loggly import logger


class SBaseModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    isDeleted: Optional[bool]
    deletedAt: Optional[datetime]

    def __init__(self, **pydict):
        try:
            super().__init__(**pydict)
            self.id = pydict.pop("_id")
        except Exception as e:
            logger.error(f"Error while mapping the id to record - {e}")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: datetime.isoformat,
        }
