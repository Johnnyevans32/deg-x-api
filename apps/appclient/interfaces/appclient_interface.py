from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pymongo import ASCENDING

from core.db import db
from core.depends.model import SBaseModel


class AppClientAuth(BaseModel):
    clientID: Optional[str]
    clientSecret: Optional[str]


class AppClientIn(AppClientAuth):
    name: str
    callBackUrl: Optional[str]
    appUrl: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "demi-chee",
                "callBackUrl": "demigod.com/callback",
                "appUrl": "demigod.com",
            }
        }


class AppClient(SBaseModel):
    name: str
    clientID: str
    clientSecret: str
    callBackUrl: str
    appUrl: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @staticmethod
    def init():
        db.appclient.create_index([("name", ASCENDING)], unique=True)
