from bson import ObjectId
from pydantic import BaseModel


class MongoModel(BaseModel):

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    @classmethod
    def from_mongo(cls, data: dict):
        """We must convert _id into "id". """
        if not data:
            return data
        mid = data.pop('_id', None)
        return cls(**dict(data, id=mid))

    def mongo(self, add_id: bool = False, **kwargs):
        exclude_none = kwargs.pop('exclude_none', True)
        by_alias = kwargs.pop('by_alias', True)

        parsed = self.dict(
            exclude_none=exclude_none,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = parsed.pop('id')
        if '_id' not in parsed and 'id' not in parsed and add_id:
            parsed['_id'] = ObjectId()
        return parsed

    def __init__(self, **pydict):
        super().__init__(**pydict)
        if pydict.get('_id'):
            self.id = pydict.pop('_id')
