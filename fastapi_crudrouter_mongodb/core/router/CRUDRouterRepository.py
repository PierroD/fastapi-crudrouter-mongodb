from typing import Union
from bson import ObjectId
from pydantic import BaseModel
from ..models.mongo_model import MongoModel
from ..models.deleted_mongo_model import DeletedModelOut


async def get_all(
    db, model: MongoModel, collection_name, model_out: Union[BaseModel, None]
) -> list:
    """
    Get all documents from the database

    :param db: The database to be used.
    :type db: Database
    :param model: The model to be used.
    :type model: MongoModel
    :param collection_name: The name of the collection to be used.
    :type collection_name: str
    :return: A list of documents from the database.
    :rtype: list
    """
    documents = []
    async for document in db[collection_name].find():
        mongo_model = model.from_mongo(document)
        if model_out is not None:
            mongo_model = mongo_model.convert_to(model=model_out)
        documents.append(mongo_model)
    return documents


async def get_one(
    db,
    model: MongoModel,
    collection_name: str,
    id: str,
    model_out: Union[BaseModel, None],
):
    """
    Get one document from the database

    :param db: The database to be used.
    :type db: Database
    :param model: The model to be used.
    :type model: MongoModel
    :param collection_name: The name of the collection to be used.
    :type collection_name: str
    :param id: The id of the document to be retrieved.
    :type id: str
    :return: The document from the database.
    :rtype: dict
    """
    response = await db[collection_name].find_one({"_id": ObjectId(id)})
    return (
        model.from_mongo(response)
        if model_out is None
        else model.from_mongo(response).convert_to(model=model_out)
    )


async def create_one(
    db,
    model: MongoModel,
    collection_name,
    data: MongoModel,
    model_out: Union[BaseModel, None],
):
    """
    Create one document in the database

    :param db: The database to be used.
    :type db: Database
    :param model: The model to be used.
    :type model: MongoModel
    :param collection_name: The name of the collection to be used.
    :type collection_name: str
    :param data: The data of the document to be created.
    :type data: dict
    :return: The created document.
    :rtype: dict
    """
    response = await db[collection_name].insert_one(data.to_mongo())
    response = await db[collection_name].find_one({"_id": response.inserted_id})
    return (
        model.from_mongo(response)
        if model_out is None
        else model.from_mongo(response).convert_to(model=model_out)
    )


async def replace_one(
    db,
    model: MongoModel,
    collection_name,
    id: str,
    data: MongoModel,
    model_out: Union[BaseModel, None],
):
    """
    Update one document in the database

    :param db: The database to be used.
    :type db: Database
    :param model: The model to be used.
    :type model: MongoModel
    :param collection_name: The name of the collection to be used.
    :type collection_name: str
    :param id: The id of the document to be replaced.
    :type id: str
    :param data: The data of the document to be replaced.
    :type data: dict
    :return: The replaced document.
    :rtype: dict
    """
    response = await db[collection_name].replace_one(
        {"_id": ObjectId(id)}, data.to_mongo()
    )
    response = await db[collection_name].find_one(
        {
            "_id": response.upserted_id
            if response.upserted_id is not None
            else ObjectId(id)
        }
    )
    return (
        model.from_mongo(response)
        if model_out is None
        else model.from_mongo(response).convert_to(model=model_out)
    )


async def update_one(
    db,
    model: MongoModel,
    collection_name,
    id: str,
    data: MongoModel,
    model_out: Union[BaseModel, None],
):
    """
    Update one document in the database

    :param db: The database to be used.
    :type db: Database
    :param model: The model to be used.
    :type model: MongoModel
    :param collection_name: The name of the collection to be used.
    :type collection_name: str
    :param id: The id of the document to be updated.
    :type id: str
    :param data: The data of the document to be updated.
    :type data: dict
    :return: The updated document.
    :rtype: dict
    """
    response = await db[collection_name].update_one(
        {"_id": ObjectId(id)}, {"$set": data.to_mongo()}
    )
    response = await db[collection_name].find_one(
        {
            "_id": response.upserted_id
            if response.upserted_id is not None
            else ObjectId(id)
        }
    )
    return (
        model.from_mongo(response)
        if model_out is None
        else model.from_mongo(response).convert_to(model=model_out)
    )


async def delete_one(db, collection_name, id):
    """
    Delete one document from the database

    :param db: The database to be used.
    :type db: Database
    :param collection_name: The name of the collection to be used.
    :type collection_name: str
    :param id: The id of the document to be deleted.
    :type id: str
    :return: The id of the deleted document.
    :rtype: dict
    """
    await db[collection_name].delete_one({"_id": ObjectId(id)})
    return DeletedModelOut.from_mongo({"_id": id})
