from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from pymongo import ASCENDING

from apps.country.interfaces.country_interface import Country
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class Name(BaseModel):
    first: str
    last: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class SignUpMethod(str, Enum):
    GOOGLE = "google-oauth"
    EMAIL = "email-signup"


class UserLoginInput(BaseModel):
    password: str
    email: EmailStr

    model_config = ConfigDict(
        str_to_lower=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {"email": "evans@demigod.com", "password": "password"}
        },
    )


class UserResetPasswordInput(BaseModel):
    password: str


class Username(BaseModel):
    username: Optional[str] = None

    model_config = ConfigDict(str_to_lower=True, str_strip_whitespace=True)


class UserUpdateDTO(Username):
    name: Optional[Name] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class UserBase(UserUpdateDTO, SBaseOutModel):
    email: EmailStr
    qrImage: Optional[str] = None
    country: Optional[Union[PyObjectId, Country]] = None

    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)


class User(UserBase, SBaseModel):
    password: Optional[str] = None
    socketIds: list[str] = Field(default=[])
    isVerified: bool = Field(default=False)
    signUpMethod: SignUpMethod = Field(
        default=SignUpMethod.EMAIL,
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
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
        },
    )

    @staticmethod
    def init() -> None:
        db.user.create_index([("email", ASCENDING)], unique=True)
