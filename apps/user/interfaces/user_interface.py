from enum import Enum
from typing import Any, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field
from pymongo import ASCENDING

from apps.country.interfaces.country_interface import Country
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel
from core.utils.loggly import logger


class Name(BaseModel):
    first: str
    last: str


class SignUpMethod(str, Enum):
    google = "google-oauth"
    email = "email-signup"


class UserLoginInput(BaseModel):
    password: str
    email: Optional[EmailStr]

    def __init__(self, email: EmailStr, **data: Any):
        super().__init__(**data)
        self.email = EmailStr(email.strip().lower())

    class Config:
        schema_extra = {
            "example": {"email": "evans@demigod.com", "password": "password"}
        }


class UserResetPasswordInput(BaseModel):
    password: str


class AbstractUser(UserLoginInput):
    name: Optional[Name]
    isVerified: bool = Field(default=False)
    username: Optional[str]
    country: Optional[Union[Country, PyObjectId]]
    signUpMethod: Optional[SignUpMethod] = Field(hidden_from_schema=True)

    def __init__(self, name: Any, username: str, **data: Any):
        super().__init__(**data)
        self.name = Name(first=name["first"].strip(), last=name["last"].strip())
        self.username = username.strip()

    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "name": {
                    "first": "demigod",
                    "last": "evans",
                },
                "email": "evans@demigod.com",
                "password": "password",
                "username": "sss",
                "country": "61689fc4dc4f8ba4c07f52e2",
            }
        }


class UserOut(SBaseModel):
    name: Name
    isVerified: bool
    username: str
    email: str

    class Config:
        schema_extra = {
            "example": {
                "name": {
                    "first": "demigod",
                    "last": "evans",
                },
                "email": "evans@demigod.com",
                "username": "sss",
            }
        }


class User(SBaseModel):
    name: Name
    email: EmailStr
    username: Optional[str]
    password: str
    isVerified: bool = Field(default=False)
    country: Optional[Union[PyObjectId, Country]]
    signUpMethod: SignUpMethod

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @staticmethod
    def init():
        db.user.create_index([("email", ASCENDING)], unique=True)
