from bson import ObjectId
from pydantic_core import core_schema
from typing import Any
from pydantic.json_schema import JsonSchemaValue


class MongoObjectId(ObjectId):
    @classmethod
    def validate_object_id(cls, field: Any, handler) -> ObjectId:
        if isinstance(field, ObjectId):
            return field

        value = handler(field)
        if ObjectId.is_valid(value):
            return ObjectId(value)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, _handler
    ) -> core_schema.CoreSchema:
        assert source_type is ObjectId
        return core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())
