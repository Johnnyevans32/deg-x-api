from typing import Optional

from pymongo import ASCENDING
from pydantic import ConfigDict
from core.db import db
from core.depends.model import SBaseModel


class AppClient(SBaseModel):
    name: str
    callBackUrl: Optional[str] = None
    appUrl: str
    clientID: Optional[str] = None
    clientSecret: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Deg X",
                "callBackUrl": "https://string.com",
                "appUrl": "https://string.com",
            }
        }
    )

    ConfigDict

    @staticmethod
    def init() -> None:
        db.appclient.create_index([("name", ASCENDING)], unique=True)
