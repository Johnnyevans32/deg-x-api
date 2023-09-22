# fix ObjectId & FastApi conflict
from typing import Any

from bson.objectid import ObjectId


# https://python.plainenglish.io/how-to-use-fastapi-with-mongodb-75b43c8e541d
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid objectid")
        return ObjectId(str(v))

    @classmethod
    def __modify_schema__(cls, field_schema: Any) -> None:
        field_schema.update(type="string")
