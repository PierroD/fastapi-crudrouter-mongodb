from .mongo_model import MongoModel
from pydantic import BaseModel


class CRUDPopulate:
    """
    Configuration object for automatic reference population on CRUDRouter.

    :param field: Name of the field containing ObjectId references.
    :type field: str
    :param collection: Target collection where referenced documents are stored.
    :type collection: str
    :param model: MongoModel subclass used to deserialize resolved documents.
    :type model: type
    :param model_out: Optional output schema used to serialize resolved documents.
    :type model_out: type[BaseModel] | None
    :raises ValueError: If ``field`` or ``collection`` is empty.
    :raises ValueError: If ``model`` is not a ``MongoModel`` subclass.
    :raises ValueError: If ``model_out`` is provided and is not a ``BaseModel`` subclass.
    """

    def __init__(
        self,
        field: str,
        collection: str,
        model: type,
        model_out: type[BaseModel] | None = None,
    ) -> None:
        if not isinstance(field, str) or not field.strip():
            raise ValueError("CRUDPopulate: 'field' must be a non-empty string")
        if not isinstance(collection, str) or not collection.strip():
            raise ValueError("CRUDPopulate: 'collection' must be a non-empty string")
        if not (isinstance(model, type) and issubclass(model, MongoModel)):
            raise ValueError(
                f"CRUDPopulate: 'model' must be a subclass of MongoModel, got {model!r}"
            )
        if model_out is not None and not (
            isinstance(model_out, type) and issubclass(model_out, BaseModel)
        ):
            raise ValueError(
                "CRUDPopulate: 'model_out' must be a subclass of BaseModel when provided"
            )

        self.field = field
        self.collection = collection
        self.model = model
        self.model_out = model_out
