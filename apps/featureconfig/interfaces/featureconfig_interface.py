from enum import Enum

from bson import ObjectId
from pydantic import Field
from pydantic.main import BaseModel
from pymongo import ASCENDING

from core.db import db
from core.depends.model import SBaseModel


class FeatureName(str, Enum):
    SignUpBonus = "sign-up-bonus"


class FeatureStatusUpdateDTO(BaseModel):
    status: bool


class FeatureConfig(SBaseModel):
    name: FeatureName
    isEnabled: bool = Field(default=False)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @staticmethod
    def init():
        db.featureconfig.create_index([("name", ASCENDING)], unique=True)
