from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel
from pymongo import ASCENDING

from core.db import db
from core.depends.model import SBaseModel


class FeatureName(str, Enum):
    SIGNUPBONUS = "sign-up-bonus"


class FeatureStatusUpdateDTO(BaseModel):
    status: bool


class FeatureConfig(SBaseModel):
    name: FeatureName
    isEnabled: bool = Field(default=False)

    @staticmethod
    def init() -> None:
        db.featureconfig.create_index([("name", ASCENDING)], unique=True)
