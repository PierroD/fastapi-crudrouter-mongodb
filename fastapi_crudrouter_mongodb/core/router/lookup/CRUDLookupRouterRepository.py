from bson import ObjectId
from ...models.mongo_model import MongoModel


async def get_all(db, collection_name: str, id: str, foreign_field: str, local_field: str, parent_collection_name: str, parent_model: MongoModel) -> list:
    """
    Get all documents from the database with a lookup
    """
    documents = db[parent_collection_name].aggregate([
        {
            '$match': {
                '_id': ObjectId(id)
            }
        }, {
            '$lookup': {
                'from': collection_name,
                'localField': local_field,
                'foreignField': foreign_field,
                'as': collection_name
            }
        }
    ])
    models = []
    async for document in documents:
        models.append(parent_model.from_mongo(document))
    return models[0]


async def get_one(db, collection_name: str, id: str, lookup_id: str, foreign_field: str, local_field: str, parent_collection_name: str, parent_model: MongoModel) -> MongoModel:
    """
    Get one document from the database with a lookup
    """
    documents = db[parent_collection_name].aggregate(
        [
            {'$match': {'_id': ObjectId(id)}},
            {
                '$lookup': {
                    'from': collection_name,
                    'localField': local_field,
                    'foreignField': foreign_field,
                    'as': collection_name,
                    'pipeline': [{'$match': {'_id': ObjectId(lookup_id)}}],
                }
            },
            {
                '$unwind': {
                    'path': f'${collection_name}',
                    'preserveNullAndEmptyArrays': True,
                }
            },
        ]
    )
    models = []
    async for document in documents:
        models.append(parent_model.from_mongo(document))
    return models[0]


async def create_one(db, collection_name: str, id: str, data, foreign_field: str, local_field: str, parent_collection_name: str, parent_model: MongoModel) -> MongoModel:
    """
    Create one document in the database with a lookup
    """
    print(data)
    response = await db[collection_name].insert_one(data.mongo())
    return await get_one(db, collection_name, id, response.inserted_id, foreign_field, local_field, parent_collection_name, parent_model)


async def replace_one(db, collection_name: str, id: str, lookup_id: str, data, foreign_field: str, local_field: str, parent_collection_name: str, parent_model: MongoModel) -> MongoModel:
    """
    Update one document in the database with a lookup
    """
    response = await db[collection_name].replace_one({"_id": ObjectId(lookup_id)}, data.mongo())
    return await get_one(db, collection_name, id, lookup_id, foreign_field, local_field, parent_collection_name, parent_model)


async def update_one(db, collection_name: str, id: str, lookup_id: str, data, foreign_field: str, local_field: str, parent_collection_name: str, parent_model: MongoModel) -> MongoModel:
    """
    Update one document in the database with a lookup
    """
    response = await db[collection_name].update_one({"_id": ObjectId(lookup_id)}, {"$set": data.mongo()})
    return await get_one(db, collection_name, id, lookup_id, foreign_field, local_field, parent_collection_name, parent_model)


async def delete_one(db, collection_name: str, id: str, lookup_id: str, foreign_field: str, local_field: str, parent_collection_name: str, parent_model: MongoModel) -> MongoModel:
    """
    Delete one document in the database with a lookup
    """
    response = await db[collection_name].delete_one({"_id": ObjectId(lookup_id)})
    return await get_one(db, collection_name, id, lookup_id, foreign_field, local_field, parent_collection_name, parent_model)
