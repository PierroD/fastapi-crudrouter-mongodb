from typing import Any, Callable
from fastapi import HTTPException, status
from ..models.deleted_mongo_model import DeletedModelOut
from pydantic import BaseModel
from . import CRUDRouterRepository


class CRUDRouterService:
    """
    CRUDRouterService is a class that implements the CRUD operations for a given model.

    This class initializes the necessary components for performing CRUD operations on a specified
    MongoDB collection using the provided model and database.

    :param model: The Pydantic model to be used for the CRUD operations.
    :type model: BaseModel
    :param db: The database connection instance to be used for the CRUD operations.
    :type db: Database
    :param collection_name: The name of the collection within the database to be used for the CRUD operations.
    :type collection_name: str
    :param model_out: (Optional) The Pydantic model to be used for output validation and serialization.
    :type model_out: BaseModel | None
    :param args: Additional arguments to be passed to the CRUD operations.
    :type args: Any
    :param kwargs: Additional keyword arguments to be passed to the CRUD operations.
    :type kwargs: Any
    """

    def __init__(
        self,
        model,
        db,
        collection_name: str,
        model_out: BaseModel | None = None,
        *args,
        **kwargs
    ) -> None:
        self.model = model
        self.db = db
        self.collection_name = collection_name
        self.model_out = model_out

    async def get_all(self, *args: Any, **kwargs: Any) -> list[Any]:
        """
        Get all documents from the collection.

        :return: A list of documents from the collection.
        :rtype: list
        """
        response = await CRUDRouterRepository.get_all(
            self.db, self.model, self.collection_name, self.model_out
        )
        return response if len(response) else []

    async def get_one(self, id: str, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Get one document from the collection.

        :param id: The id of the document to be retrieved.
        :type id: str
        :return: The document from the collection.
        :rtype: dict
        """
        response = await CRUDRouterRepository.get_one(
            self.db, self.model, self.collection_name, id, self.model_out
        )
        if response is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Document not found")

        return response

    async def create_one(self, data, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Create one document in the collection.

        :param data: The data of the document to be created.
        :type data: dict
        :return: The created document.
        :rtype: dict
        """
        response = await CRUDRouterRepository.create_one(
            self.db, self.model, self.collection_name, data, self.model_out
        )
        if response is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Document not created"
            )
        return response

    async def replace_one(
        self, id: str, data, *args: Any, **kwargs: Any
    ) -> Callable[..., Any]:
        """
        Replace one document in the collection.

        :param id: The id of the document to be replaced.
        :type id: str
        :param data: The data of the document to be replaced.
        :type data: dict
        :return: The replaced document.
        :rtype: dict
        """
        response = await CRUDRouterRepository.replace_one(
            self.db, self.model, self.collection_name, id, data, self.model_out
        )
        if response is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Document not replaced"
            )
        return response

    async def update_one(
        self, id: str, data, *args: Any, **kwargs: Any
    ) -> Callable[..., Any]:
        """
        Update one document in the collection.

        :param id: The id of the document to be updated.
        :type id: str
        :param data: The data of the document to be updated.
        :type data: dict
        :return: The updated document.
        :rtype: dict
        """
        response = await CRUDRouterRepository.update_one(
            self.db, self.model, self.collection_name, id, data, self.model_out
        )
        if response is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Document not updated"
            )
        return response

    async def delete_one(self, id: str, *args: Any, **kwargs: Any) -> DeletedModelOut:
        """
        Delete one document from the collection.

        :param id: The id of the document to be deleted.
        :type id: str
        :return: The deleted document id.
        :rtype: dict {"id": "{deleted_id}"}
        """
        response = await CRUDRouterRepository.delete_one(
            self.db, self.collection_name, id
        )
        if response is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Document not deleted"
            )
        return response
