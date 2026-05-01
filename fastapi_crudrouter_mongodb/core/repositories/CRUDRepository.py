from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel
from pymongo import ReturnDocument
from ..models.mongo_model import MongoModel
from ..utils.sorting import normalize_order_by
from ..utils.deprecated_util import deprecated


class CRUDRepository:

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
        self.identifier_field = self._to_lower_camel_case(identifier_field)
        self.model_out = model_out

    def _to_camel_case(self, snake_str):
        return "".join(x.capitalize() for x in snake_str.lower().split("_"))

    def _to_lower_camel_case(self, snake_str):
        if snake_str.startswith("_"):
            # Prevent to capitalize Mongo keys, like _id
            return snake_str

        # We capitalize the first letter of each component except the first one
        # with the 'capitalize' method and join them together.
        camel_string = self._to_camel_case(snake_str)
        return snake_str[0].lower() + camel_string[1:]

    def _is_valid_objectid(self, value):
        try:
            ObjectId(value)
            return True
        except (InvalidId, TypeError):
            return False

    def _get_identifier_value(self, value):
        if self._is_valid_objectid(value):
            return ObjectId(value)
        return value

    @deprecated("get_all is deprecated. Use find_all instead.")
    async def get_all(self) -> list:
        return await self.find_all()

    async def find_all(
        self,
        skip: int | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        order_by: str | None = None,
        filters: dict | None = None,
        apply_model_out: bool = True,
    ) -> list:
        """
        Find all documents from the database.

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

        :return: A list of documents from the database.
        :rtype: list
        """
        documents = []
        cursor = self.db[self.collection_name].find(filters or {})
        if sort_by is not None:
            cursor = cursor.sort(sort_by, normalize_order_by(order_by))
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        async for document in cursor:
            mongo_model = self.model.from_mongo(document)
            if self.model_out is not None and apply_model_out:
                mongo_model = mongo_model.convert_to(model=self.model_out)
            documents.append(mongo_model)
        return documents

    @deprecated("get_one is deprecated. Use find_one instead.")
    async def get_one(self, id):
        return await self.find_one(id)

    async def find_one(
        self,
        id: str,
        apply_model_out: bool = True,
    ):
        """
        Find one document from the database

        :type id: str
        :return: The document from the database.
        :rtype: dict
        """
        identifier_value = self._get_identifier_value(id)
        response = await self.db[self.collection_name].find_one(
            {f"{self.identifier_field}": identifier_value}
        )
        if response is None:
            return None
        return (
            self.model.from_mongo(response)
            if self.model_out is None or not apply_model_out
            else self.model.from_mongo(response).convert_to(model=self.model_out)
        )

    async def create_one(
        self,
        data: MongoModel,
    ):
        """
        Create one document in the database

        :param data: The data of the document to be created.
        :type data: dict
        :return: The created document.
        :rtype: dict
        """
        identifier_attr = (
            "id" if self.identifier_field == "_id" else self.identifier_field
        )
        identifier_value = getattr(data, identifier_attr, None)
        if self.identifier_field is None:
            return None
        if identifier_value is not None:
            does_document_exist = await self.find_one(str(identifier_value))
            if does_document_exist:
                return None

        response = await self.db[self.collection_name].insert_one(data.to_mongo())
        response = await self.db[self.collection_name].find_one(
            {"_id": response.inserted_id}
        )
        return (
            self.model.from_mongo(response)
            if self.model_out is None
            else self.model.from_mongo(response).convert_to(model=self.model_out)
        )

    async def replace_one(
        self,
        id: str,
        data: MongoModel,
    ):
        """
        Update one document in the database

        :param id: The id of the document to be replaced.
        :type id: str
        :param data: The data of the document to be replaced.
        :type data: dict
        :return: The replaced document.
        :rtype: dict
        """
        identifier_value = self._get_identifier_value(id)
        response = await self.db[self.collection_name].find_one_and_replace(
            {f"{self.identifier_field}": identifier_value},
            data.to_mongo(),
            return_document=ReturnDocument.AFTER,
        )
        return (
            self.model.from_mongo(response)
            if self.model_out is None
            else self.model.from_mongo(response).convert_to(model=self.model_out)
        )

    async def update_one(
        self,
        id: str,
        data: MongoModel,
    ):
        """
        Update one document in the database

        :param id: The id of the document to be updated.
        :type id: str
        :param data: The data of the document to be updated.
        :type data: dict
        :return: The updated document.
        :rtype: dict
        """
        identifier_value = self._get_identifier_value(id)
        response = await self.db[self.collection_name].find_one_and_update(
            {f"{self.identifier_field}": identifier_value},
            {"$set": data.to_mongo()},
            return_document=ReturnDocument.AFTER,
        )

        return (
            self.model.from_mongo(response)
            if self.model_out is None
            else self.model.from_mongo(response).convert_to(model=self.model_out)
        )

    async def delete_one(self, id: str):
        """
        Delete one document from the database

        :param id: The id of the document to be deleted.
        :type id: str
        :return: The id of the deleted document.
        :rtype: dict
        """
        identifier_value = self._get_identifier_value(id)
        response = await self.db[self.collection_name].find_one_and_delete(
            {f"{self.identifier_field}": identifier_value}
        )
        return self.model.from_mongo(response) if (response is not None) else None

    async def resolve_populate(self, docs: list, populates: list) -> list:
        """
        Resolve ObjectId array fields in documents using batch ``$in`` queries.

        :param docs: Documents where populate fields should be resolved.
        :type docs: list
        :param populates: List of CRUDPopulate configuration objects.
        :type populates: list
        :return: Documents with resolved fields.
        :rtype: list
        :raises ValueError: If circular reference is detected.
        """
        for populate in populates:
            if populate.collection == self.collection_name:
                raise ValueError(
                    "Circular reference detected: "
                    f"populate field '{populate.field}' points to "
                    f"collection '{populate.collection}', which matches parent "
                    f"collection '{self.collection_name}'."
                )

            all_ids = []
            seen = set()
            for doc in docs:
                field_value = getattr(doc, populate.field, None)
                if not field_value:
                    continue
                for object_id in field_value:
                    key = str(object_id)
                    if key in seen:
                        continue
                    seen.add(key)
                    all_ids.append(object_id)

            if not all_ids:
                continue

            resolved_map = {}
            async for document in self.db[populate.collection].find(
                {"_id": {"$in": all_ids}}
            ):
                document_copy = dict(document)
                document_id = document_copy.get("_id")
                if document_id is None:
                    continue
                resolved_model = populate.model.from_mongo(document_copy)
                if populate.model_out is not None:
                    resolved_model = resolved_model.convert_to(model=populate.model_out)
                resolved_map[str(document_id)] = resolved_model

            for doc in docs:
                field_value = getattr(doc, populate.field, None)
                if not field_value:
                    continue
                resolved_values = [
                    resolved_map[str(object_id)]
                    for object_id in field_value
                    if str(object_id) in resolved_map
                ]
                try:
                    setattr(doc, populate.field, resolved_values)
                except Exception:
                    object.__setattr__(doc, populate.field, resolved_values)

        return docs
