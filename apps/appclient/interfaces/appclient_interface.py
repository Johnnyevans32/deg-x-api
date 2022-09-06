from typing import Optional
from pymongo import ASCENDING

from core.db import db
from core.depends.model import SBaseModel


class AppClient(SBaseModel):
    name: str
    callBackUrl: Optional[str]
    appUrl: str
    clientID: Optional[str]
    clientSecret: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "Deg X",
                "callBackUrl": "https://string.com",
                "appUrl": "https://string.com",
            }
        }

    @staticmethod
    def init() -> None:
        db.appclient.create_index([("name", ASCENDING)], unique=True)
