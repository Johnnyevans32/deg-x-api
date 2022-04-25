from typing import Optional

from bson import ObjectId
from pydantic import Field
from pymongo import ASCENDING

from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel
from core.utils.loggly import logger


class CountryOut(SBaseModel):
    name: str
    code: str
    callingCode: str
    flag: str

    class Config:
        arbitrary_types_allowed = True


class Country(SBaseModel):
    name: str
    code: str
    callingCode: str
    flag: str
    metaData: Optional[dict]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @staticmethod
    def init():
        db.country.create_index([("name", ASCENDING)], unique=True)
