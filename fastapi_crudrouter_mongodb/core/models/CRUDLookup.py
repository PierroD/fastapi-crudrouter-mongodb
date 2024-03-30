from .mongo_model import MongoModel


class CRUDLookup:
    def __init__(
        self,
        model: MongoModel,
        model_out: MongoModel,
        collection_name: str,
        prefix: str,
        local_field: str,
        foreign_field: str,
    ):
        self.model = model
        self.model_out = model_out
        self.collection_name = collection_name
        self.prefix = prefix
        self.local_field = local_field
        self.foreign_field = foreign_field
