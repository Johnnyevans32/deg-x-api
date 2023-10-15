from typing import Any, Optional

from pymongo import ASCENDING

from core.db import db
from core.depends.model import SBaseModel


class Country(SBaseModel):
    name: str
    code: str
    callingCode: str
    flag: str
    metaData: Optional[dict[str, Any]] = None

    @staticmethod
    def init() -> None:
        db.country.create_index([("name", ASCENDING)], unique=True)
