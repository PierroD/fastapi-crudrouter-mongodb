from bson import ObjectId

from ...models.mongo_model import MongoModel
from ...models.deleted_mongo_model import DeletedModelOut


async def get_all(
    db, id: str, parent_collection_name: str, embed_name: str, model: MongoModel
) -> list:
    """
    Get all embeded documents from the database
    """
    try:
        documents = db[parent_collection_name].aggregate(
            [
                {"$match": {"_id": ObjectId(id)}},
                {"$unwind": f"${embed_name}"},
                {"$replaceRoot": {"newRoot": f"${embed_name}"}},
            ]
        )

        models = []
        async for document in documents:
            models.append(model.from_mongo(document))
        return models
    except Exception:
        return []


async def get_one(
    db,
    id: str,
    embed_id: str,
    parent_collection_name: str,
    embed_name: str,
    model: MongoModel,
) -> MongoModel | None:
    """
    Get a document from the database
    """
    try:
        document = db[parent_collection_name].aggregate(
            [
                {"$match": {"_id": ObjectId(id)}},
                {"$unwind": f"${embed_name}"},
                {"$replaceRoot": {"newRoot": f"${embed_name}"}},
                {"$match": {"_id": ObjectId(embed_id)}},
            ]
        )
        models = []
        async for document in document:
            models.append(model.from_mongo(document))
        return models[0]
    except Exception:
        return None


async def create_one(
    db,
    id: str,
    parent_collection_name: str,
    embed_name: str,
    data: MongoModel,
    model: MongoModel,
) -> MongoModel:
    """
    Create a new document in the database
    """
    document_mongo = data.to_mongo(add_id=True)
    await db[parent_collection_name].update_one(
        {"_id": ObjectId(id)}, {"$push": {embed_name: document_mongo}}
    )

    return model.from_mongo(document_mongo)


async def update_one(
    db,
    id: str,
    embed_id: str,
    parent_collection_name: str,
    embed_name: str,
    data: MongoModel,
    model: MongoModel,
) -> MongoModel:
    """
    Update a document in the database
    """
    document_mongo = data.to_mongo(add_id=False)
    document_mongo["_id"] = ObjectId(embed_id)
    await db[parent_collection_name].update_one(
        {"_id": ObjectId(id), f"{embed_name}._id": ObjectId(embed_id)},
        {"$set": {f"{embed_name}.$": document_mongo}},
    )

    return model.from_mongo(document_mongo)


async def delete_one(
    db,
    id: str,
    embed_id: str,
    parent_collection_name: str,
    embed_name: str,
    model: MongoModel,
) -> DeletedModelOut | None:
    """
    Delete a document in the database
    """
    try:
        await db[parent_collection_name].update_one(
            {"_id": ObjectId(id)},
            {"$pull": {f"{embed_name}": {"_id": ObjectId(embed_id)}}},
        )
        return (
            DeletedModelOut.from_mongo({"_id": embed_id})
            if await get_one(
                db, id, embed_id, parent_collection_name, embed_name, model
            )
            is None
            else None
        )
    except Exception:
        return None
