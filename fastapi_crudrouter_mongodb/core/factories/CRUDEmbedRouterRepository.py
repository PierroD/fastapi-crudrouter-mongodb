from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Response
from ..models import DeletedModelOut
from ..models.mongo_model import MongoModel


def _parent_filter(id: str, parent_identifier_field: str) -> dict:
    """Build a MongoDB filter for the parent document using its identifier field."""
    if parent_identifier_field == "_id":
        try:
            return {"_id": ObjectId(id)}
        except (InvalidId, TypeError):
            pass
    return {parent_identifier_field: id}


def _embed_filter(embed_id: str, embed_identifier_field: str) -> dict:
    """Build a match filter for an embedded sub-document using its identifier field."""
    if embed_identifier_field == "_id":
        try:
            return {"_id": ObjectId(embed_id)}
        except (InvalidId, TypeError):
            pass
    return {embed_identifier_field: embed_id}


async def get_all(
    db,
    id: str,
    parent_collection_name: str,
    embed_name: str,
    model: MongoModel,
    skip: int | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    order_by: int = 1,
    filters: dict | None = None,
    parent_identifier_field: str = "_id",
) -> list:
    """
    Get all embeded documents from the database
    """
    try:
        pipeline = [
            {"$match": _parent_filter(id, parent_identifier_field)},
            {"$unwind": f"${embed_name}"},
            {"$replaceRoot": {"newRoot": f"${embed_name}"}},
        ]
        if filters is not None:
            pipeline.append({"$match": filters})
        if sort_by is not None:
            pipeline.append({"$sort": {sort_by: order_by}})
        if skip is not None:
            pipeline.append({"$skip": skip})
        if limit is not None:
            pipeline.append({"$limit": limit})

        documents = db[parent_collection_name].aggregate(pipeline)

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
    parent_identifier_field: str = "_id",
    embed_identifier_field: str = "_id",
) -> MongoModel | None:
    """
    Get a document from the database
    """
    try:
        document = db[parent_collection_name].aggregate(
            [
                {"$match": _parent_filter(id, parent_identifier_field)},
                {"$unwind": f"${embed_name}"},
                {"$replaceRoot": {"newRoot": f"${embed_name}"}},
                {"$match": _embed_filter(embed_id, embed_identifier_field)},
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
    parent_identifier_field: str = "_id",
) -> MongoModel:
    """
    Create a new document in the database
    """
    document_mongo = data.to_mongo(add_id=True)
    await db[parent_collection_name].update_one(
        _parent_filter(id, parent_identifier_field),
        {"$push": {embed_name: document_mongo}},
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
    parent_identifier_field: str = "_id",
    embed_identifier_field: str = "_id",
) -> MongoModel:
    """
    Update a document in the database
    """
    document_mongo = data.to_mongo(add_id=False)
    if embed_identifier_field == "_id":
        try:
            document_mongo["_id"] = ObjectId(embed_id)
        except (InvalidId, TypeError):
            document_mongo[embed_identifier_field] = embed_id
    else:
        document_mongo[embed_identifier_field] = embed_id
    parent_filter = _parent_filter(id, parent_identifier_field)
    embed_key = (
        f"{embed_name}._id"
        if embed_identifier_field == "_id"
        else f"{embed_name}.{embed_identifier_field}"
    )
    if embed_identifier_field == "_id":
        try:
            parent_filter[embed_key] = ObjectId(embed_id)
        except (InvalidId, TypeError):
            parent_filter[embed_key] = embed_id
    else:
        parent_filter[embed_key] = embed_id
    await db[parent_collection_name].update_one(
        parent_filter,
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
    parent_identifier_field: str = "_id",
    embed_identifier_field: str = "_id",
) -> Response | None:
    """
    Delete a document in the database
    """
    try:
        await db[parent_collection_name].update_one(
            _parent_filter(id, parent_identifier_field),
            {
                "$pull": {
                    f"{embed_name}": _embed_filter(embed_id, embed_identifier_field)
                }
            },
        )
        return (
            DeletedModelOut.from_mongo({"_id": embed_id})
            if await get_one(
                db,
                id,
                embed_id,
                parent_collection_name,
                embed_name,
                model,
                parent_identifier_field,
                embed_identifier_field,
            )
            is None
            else None
        )
    except Exception:
        return None
