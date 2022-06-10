from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field
from pymongo import ASCENDING
from apps.country.interfaces.country_interface import Country
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class Name(BaseModel):
    first: str
    last: str

    class Config:
        anystr_strip_whitespace = True


class SignUpMethod(str, Enum):
    GOOGLE = "google-oauth"
    EMAIL = "email-signup"


class UserLoginInput(BaseModel):
    password: str
    email: Optional[EmailStr]

    class Config:
        schema_extra = {
            "example": {"email": "evans@demigod.com", "password": "password"}
        }


class UserResetPasswordInput(BaseModel):
    password: str


class UserBase(BaseModel):
    name: Name
    email: EmailStr
    username: str
    country: Optional[Union[PyObjectId, Country]]


class UserOut(UserBase, SBaseOutModel):
    class Config:
        anystr_strip_whitespace = True


class User(UserBase, SBaseModel):
    password: str = Field(hidden_from_schema=True)
    isVerified: bool = Field(default=False, hidden_from_schema=True)
    signUpMethod: SignUpMethod = Field(
        default=SignUpMethod.EMAIL, hidden_from_schema=True
    )

    class Config:
        anystr_strip_whitespace = True
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

    @staticmethod
    def init():
        db.user.create_index([("email", ASCENDING)], unique=True)
