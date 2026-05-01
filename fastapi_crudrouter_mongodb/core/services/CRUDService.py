from typing import Any, Callable
from fastapi import HTTPException, status, Response
from pydantic import BaseModel
from ..repositories import CRUDRepository
from ..utils.deprecated_util import deprecated


class CRUDService:
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
        identifier_field: str = "_id",
        model_out: BaseModel | None = None,
        *args,
        **kwargs,
    ) -> None:
        self.model = model
        self.db = db
        self.collection_name = collection_name
        self.identifier_field = identifier_field
        self.model_out = model_out
        self.repository = CRUDRepository(
            model=model,
            db=db,
            collection_name=collection_name,
            identifier_field=identifier_field,
            model_out=model_out,
        )

    @deprecated("get_all is deprecated. Use find_all instead.")
    async def get_all(self, *args: Any, **kwargs: Any) -> list[Any]:
        return await self.find_all(*args, **kwargs)

    async def find_all(
        self,
        skip: int | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        order_by: str | None = None,
        filters: dict | None = None,
        populates: list | None = None,
    ) -> list[Any]:
        """
        Find all documents from the collection.

        :param skip: Optional number of documents to skip.
        :type skip: int | None
        :param limit: Optional maximum number of documents to return.
        :type limit: int | None
        :param sort_by: Field name used for sorting.
        :type sort_by: str | None
        :param order_by: Sort order, ``ASC`` for ascending or ``DESC`` for descending.
        :type order_by: str | None
        :param filters: MongoDB filter document.
        :type filters: dict | None
        :param populates: List of CRUDPopulate configuration objects.
        :type populates: list | None

        :return: A list of documents from the collection.
        :rtype: list
        """
        response = await self.repository.find_all(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            order_by=order_by,
            filters=filters,
            apply_model_out=not bool(populates),
        )
        if populates:
            try:
                response = await self.repository.resolve_populate(response, populates)
            except ValueError as e:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    str(e),
                ) from e
            populated_payloads = [
                self._serialize_populated_fields(doc, populates) for doc in response
            ]
            if self.model_out is not None:
                response = [doc.convert_to(model=self.model_out) for doc in response]
            return [
                self._serialize_populated_document(
                    doc, populates, populated_payloads[i]
                )
                for i, doc in enumerate(response)
            ]
        return response if len(response) else []

    @deprecated("get_one is deprecated. Use find_one instead.")
    async def get_one(self, id: str, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return await self.find_one(id, *args, **kwargs)

    async def find_one(
        self,
        id: str,
        *args: Any,
        populates: list | None = None,
        **kwargs: Any,
    ) -> Callable[..., Any]:
        """
        Find one document from the collection.

        :param id: The id of the document to be retrieved.
        :type id: str
        :return: The document from the collection.
        :rtype: dict
        """
        response = await self.repository.find_one(
            id,
            apply_model_out=not bool(populates),
        )
        if response is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Document not found")

        if populates:
            try:
                response = (
                    await self.repository.resolve_populate([response], populates)
                )[0]
            except ValueError as e:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    str(e),
                ) from e
            populated_payload = self._serialize_populated_fields(response, populates)
            if self.model_out is not None:
                response = response.convert_to(model=self.model_out)
            return self._serialize_populated_document(
                response,
                populates,
                populated_payload,
            )

        return response

    def _serialize_populated_document(
        self,
        doc: BaseModel,
        populates: list,
        populated_payload: dict[str, Any] | None = None,
    ) -> dict:
        """Serialize a populated document while forcing populated fields to JSON objects."""
        serialized = doc.model_dump(by_alias=True, mode="json")
        for populate in populates:
            field_info = doc.__class__.model_fields.get(populate.field)
            output_field = (
                field_info.alias if field_info and field_info.alias else populate.field
            )
            if populated_payload is not None and populate.field in populated_payload:
                serialized[output_field] = populated_payload[populate.field]
                continue
            field_value = getattr(doc, populate.field, None)
            serialized[output_field] = self._serialize_populate_value(field_value)
        return serialized

    def _serialize_populated_fields(
        self, doc: BaseModel, populates: list
    ) -> dict[str, Any]:
        return {
            populate.field: self._serialize_populate_value(
                getattr(doc, populate.field, None)
            )
            for populate in populates
        }

    def _serialize_populate_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, list):
            return [self._serialize_populate_value(item) for item in value]
        if isinstance(value, BaseModel):
            return value.model_dump(by_alias=True, mode="json")
        return value

    async def create_one(self, data, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Create one document in the collection.

        :param data: The data of the document to be created.
        :type data: dict
        :return: The created document.
        :rtype: dict
        """
        response = await self.repository.create_one(data)
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
        response = await self.repository.replace_one(id, data)
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
        response = await self.repository.update_one(id, data)
        if response is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Document not updated"
            )
        return response

    async def delete_one(self, id: str, *args: Any, **kwargs: Any) -> Response:
        """
        Delete one document from the collection.

        :param id: The id of the document to be deleted.
        :type id: str
        :return: The deleted document id.
        :rtype: dict {"id": "{deleted_id}"}
        """
        response = await self.repository.delete_one(id)
        if response is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Document not deleted"
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
