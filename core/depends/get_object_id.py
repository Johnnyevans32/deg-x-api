# fix ObjectId & FastApi conflict
from typing import Any

# import pydantic
from bson.objectid import ObjectId


# https://python.plainenglish.io/how-to-use-fastapi-with-mongodb-75b43c8e541d
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: Any) -> None:
        field_schema.update(type="string")


# # noinspection PyUnresolvedReferences
# pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str
# # noinspection PyUnresolvedReferences
# pydantic.json.ENCODERS_BY_TYPE[PyObjectId] = str
