from bson import ObjectId
from ..models.mongo_model import MongoModel


async def get_all(db, model: MongoModel, collection_name) -> list:
    """
    Get all documents from the database
    """
    documents = []
    async for document in db[collection_name].find():
        documents.append(model.from_mongo(document))
    return documents


async def get_one(db, model: MongoModel, collection_name: str, id: str):
    """
    Get one document from the database
    """
    response = await db[collection_name].find_one({"_id": ObjectId(id)})
    return model.from_mongo(response) if response is not None else None


async def create_one(db, model: MongoModel, collection_name, data: MongoModel):
    """
    Create one document in the database
    """
    response = await db[collection_name].insert_one(data.mongo())
    response = await db[collection_name].find_one({"_id": response.inserted_id})
    return model.from_mongo(response)


async def replace_one(db, model: MongoModel, collection_name, id: str, data: MongoModel):
    """
    Update one document in the database
    """
    response = await db[collection_name].replace_one({"_id": ObjectId(id)}, data.mongo())
    response = await db[collection_name].find_one({"_id": response.upserted_id if response.upserted_id is not None else ObjectId(id)})
    return model.from_mongo(response)


async def update_one(db, model: MongoModel, collection_name, id: str, data: MongoModel):
    """
    Update one document in the database
    """
    response = await db[collection_name].update_one({"_id": ObjectId(id)}, {"$set": data.mongo()})
    response = await db[collection_name].find_one({"_id": response.upserted_id if response.upserted_id is not None else ObjectId(id)})
    return model.from_mongo(response)


async def delete_one(db, collection_name, id):
    """
    Delete one document from the database
    """
    await db[collection_name].delete_one({"_id": ObjectId(id)})
    return {"id": id}
