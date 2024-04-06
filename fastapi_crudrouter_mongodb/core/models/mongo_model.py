from bson import ObjectId
from pydantic import BaseModel

from fastapi_crudrouter_mongodb.core.utils.deprecated_util import deprecated


class MongoModel(BaseModel):
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

    @classmethod
    def from_mongo(cls, data: dict):
        """We must convert _id into "id"."""
        if not data:
            return data
        mid = data.pop("_id", None)
        return cls(**dict(data, id=mid))

    @deprecated("use new method 'to_mongo' instead")
    def mongo(self, add_id: bool = False, **kwargs):
        exclude_none = kwargs.pop("exclude_none", True)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_none=exclude_none,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = parsed.pop("id")
        if "_id" not in parsed and "id" not in parsed and add_id:
            parsed["_id"] = ObjectId()
        return parsed

    def to_mongo(self, add_id: bool = False, by_alias: bool = False, **kwargs):
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_none=True,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = parsed.pop("id")
        if "_id" not in parsed and "id" not in parsed and add_id:
            parsed["_id"] = ObjectId()
        return parsed

    def convert_to(self, model: BaseModel):
        """Convert the current model into another model."""
        dump_model = self.model_dump()
        new_model = {}
        for field in dump_model:
            value = dump_model[field]
            if(value is not None):
                new_model[field] = value if type(value) is not ObjectId else str(value) 
                
        return model(**new_model)


    def __init__(self, **pydict):
        super().__init__(**pydict)
        if pydict.get("_id"):
            self.id = pydict.pop("_id")
