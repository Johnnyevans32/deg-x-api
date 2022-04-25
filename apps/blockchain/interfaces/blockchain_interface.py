from typing import Any

from bson import ObjectId
from pydantic import Field

from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel
from core.utils.loggly import logger


class Blockchain(SBaseModel):
    name: str
    registryName: str
    meta: dict[str, Any]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
