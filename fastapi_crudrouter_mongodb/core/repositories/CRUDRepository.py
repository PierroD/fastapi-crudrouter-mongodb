from typing import Union
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel
from pymongo import ReturnDocument
from ..models.mongo_model import MongoModel
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
            **kwargs
    ) -> None:
        self.model = model
        self.db = db
        self.collection_name = collection_name
        self.identifier_field = self._to_lower_camel_case(identifier_field)
        self.model_out = model_out


    def _to_camel_case(self, snake_str):
        return "".join(x.capitalize() for x in snake_str.lower().split("_"))

    def _to_lower_camel_case(self, snake_str):
        if(snake_str.startswith("_")):
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
        if(self._is_valid_objectid(value)):
            return ObjectId(value)
        return value

    @deprecated("get_all is deprecated. Use find_all instead.")
    async def get_all(self) -> list:
        return self.find_all()

    async def find_all(self) -> list:
        """
        Get all documents from the database

        :return: A list of documents from the database.
        :rtype: list
        """
        documents = []
        async for document in self.db[self.collection_name].find():
            mongo_model = self.model.from_mongo(document)
            if self.model_out is not None:
                mongo_model = mongo_model.convert_to(model=self.model_out)
            documents.append(mongo_model)
        return documents

    @deprecated("get_one is deprecated. Use find_one instead.")
    async def get_one(self, id):
        return self.find_one(id)

    async def find_one(
        self,
        id: str,
    ):
        """
        Get one document from the database

        :type id: str
        :return: The document from the database.
        :rtype: dict
        """
        identifier_value = self._get_identifier_value(id)
        response = await self.db[self.collection_name].find_one({f"{self.identifier_field}": identifier_value})
        if(response is None):
            return None
        return (
            self.model.from_mongo(response)
            if self.model_out is None
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
        identifier_value = getattr(data, self.identifier_field, None)
        if(self.identifier_field is None):
            return None
        does_document_exist = await self.find_one(identifier_value)
        if(does_document_exist):
            return None

        response = await self.db[self.collection_name].insert_one(data.to_mongo())
        response = await self.db[self.collection_name].find_one({"_id": response.inserted_id})
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
            {f"{self.identifier_field}" : identifier_value}, data.to_mongo(), return_document=ReturnDocument.AFTER
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
            {f"{self.identifier_field}" : identifier_value}, {"$set":data.to_mongo()}, return_document=ReturnDocument.AFTER
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
            {f"{self.identifier_field}" : identifier_value}
        )
        return self.model.from_mongo(response) if(response is not None) else None
