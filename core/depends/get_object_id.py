# fix ObjectId & FastApi conflict
from typing import Any, Callable
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from bson.objectid import ObjectId


# https://python.plainenglish.io/how-to-use-fastapi-with-mongodb-75b43c8e541d
class PyObjectId(ObjectId):
    # @classmethod
    # def __get_validators__(cls) -> Any:
    #     yield cls.validate

    # @classmethod
    # def validate(cls, v: Any) -> ObjectId:
    #     if not ObjectId.is_valid(str(v)):
    #         raise ValueError("Invalid objectid")
    #     return ObjectId(str(v))

    @classmethod
    def validate(cls, __input_value: Any, _: core_schema.ValidationInfo) -> ObjectId:
        if not ObjectId.is_valid(str(__input_value)):
            raise ValueError("Invalid objectid")
        return ObjectId(__input_value)

    # @classmethod
    # def __modify_schema__(cls, field_schema: Any) -> None:
    #     field_schema.update(type="string")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.JsonSchema, handler: Any
    ) -> JsonSchemaValue:
        json_schema: dict[str, Any] = {}
        json_schema.update(
            type="string",
        )
        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        return core_schema.general_plain_validator_function(cls.validate)
