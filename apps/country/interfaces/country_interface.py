from typing import Any, Optional

from pydantic import Field
from pymongo import ASCENDING

from core.db import db
from core.depends.model import SBaseModel


class Country(SBaseModel):
    name: str
    code: str
    callingCode: str
    flag: str
    metaData: Optional[dict[str, Any]] = Field(hidden_from_schema=True)

    @staticmethod
    def init() -> None:
        db.country.create_index([("name", ASCENDING)], unique=True)
