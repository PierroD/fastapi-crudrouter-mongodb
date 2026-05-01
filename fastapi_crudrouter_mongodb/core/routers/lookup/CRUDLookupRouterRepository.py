from typing import Any
from bson import ObjectId

from ...models.mongo_model import MongoModel
from ...models.deleted_mongo_model import DeletedModelOut


def _matches_filters(document: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    return all(document.get(key) == value for key, value in filters.items())


def _apply_sort_skip_limit(
    documents: list[dict[str, Any]],
    sort_by: str | None,
    order_by: int,
    skip: int | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    if sort_by is not None:
        documents.sort(
            key=lambda doc: doc.get(sort_by),
            reverse=(order_by == -1),
        )
    start = skip or 0
    if limit is None:
        return documents[start:]
    return documents[start : start + limit]


async def get_all(
    db,
    collection_name: str,
    id: str,
    foreign_field: str,
    local_field: str,
    parent_collection_name: str,
    parent_model: MongoModel,
    model_out: MongoModel,
    skip: int | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    order_by: int = 1,
    filters: dict | None = None,
) -> list:
    """
    Get all documents from the database with a lookup
    """
    lookup_stage: dict[str, Any] = {
        "$lookup": {
            "from": collection_name,
            "localField": local_field,
            "foreignField": foreign_field,
            "as": collection_name,
        }
    }
    lookup_pipeline: list[dict[str, Any]] = []
    if filters is not None:
        lookup_pipeline.append({"$match": filters})
    if sort_by is not None:
        lookup_pipeline.append({"$sort": {sort_by: order_by}})
    if skip is not None:
        lookup_pipeline.append({"$skip": skip})
    if limit is not None:
        lookup_pipeline.append({"$limit": limit})
    lookup_stage["$lookup"]["pipeline"] = lookup_pipeline

    try:
        documents = db[parent_collection_name].aggregate(
            [{"$match": {"_id": ObjectId(id)}}, lookup_stage]
        )
        models = []
        async for document in documents:
            models.append(parent_model.from_mongo(document))
        returned_value = models[0]
        return returned_value.convert_to(model=model_out)
    except NotImplementedError:
        parent_document = await db[parent_collection_name].find_one(
            {"_id": ObjectId(id)}
        )
        if parent_document is None:
            return None

        local_values = parent_document.get(local_field, []) or []
        child_documents = []
        async for child in db[collection_name].find(
            {foreign_field: {"$in": local_values}}
        ):
            if _matches_filters(child, filters):
                child_documents.append(child)

        child_documents = _apply_sort_skip_limit(
            child_documents,
            sort_by=sort_by,
            order_by=order_by,
            skip=skip,
            limit=limit,
        )

        parent_document[collection_name] = child_documents
        return parent_model.from_mongo(parent_document).convert_to(model=model_out)


async def get_one(
    db,
    collection_name: str,
    id: str,
    lookup_id: str,
    foreign_field: str,
    local_field: str,
    parent_collection_name: str,
    parent_model: MongoModel,
    model_out: MongoModel,
) -> MongoModel:
    """
    Get one document from the database with a lookup
    """
    try:
        documents = db[parent_collection_name].aggregate(
            [
                {"$match": {"_id": ObjectId(id)}},
                {
                    "$lookup": {
                        "from": collection_name,
                        "localField": local_field,
                        "foreignField": foreign_field,
                        "as": collection_name,
                        "pipeline": [{"$match": {"_id": ObjectId(lookup_id)}}],
                    }
                },
                {
                    "$unwind": {
                        "path": f"${collection_name}",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
            ]
        )
        models = []
        async for document in documents:
            models.append(parent_model.from_mongo(document))
        returned_value = models[0]
        return returned_value.convert_to(model=model_out)
    except NotImplementedError:
        parent_document = await db[parent_collection_name].find_one(
            {"_id": ObjectId(id)}
        )
        if parent_document is None:
            return None

        local_values = parent_document.get(local_field, []) or []
        lookup_object_id = ObjectId(lookup_id)
        if lookup_object_id not in local_values:
            parent_document[collection_name] = None
            return parent_model.from_mongo(parent_document).convert_to(model=model_out)

        child_document = await db[collection_name].find_one(
            {foreign_field: lookup_object_id}
        )
        parent_document[collection_name] = child_document
        return parent_model.from_mongo(parent_document).convert_to(model=model_out)


async def create_one(
    db,
    collection_name: str,
    id: str,
    data,
    foreign_field: str,
    local_field: str,
    parent_collection_name: str,
    parent_model: MongoModel,
    model_out: MongoModel,
) -> MongoModel:
    """
    Create one document in the database with a lookup
    """
    response = await db[collection_name].insert_one(data.to_mongo())
    return await get_one(
        db,
        collection_name,
        id,
        response.inserted_id,
        foreign_field,
        local_field,
        parent_collection_name,
        parent_model,
        model_out,
    )


async def replace_one(
    db,
    collection_name: str,
    id: str,
    lookup_id: str,
    data,
    foreign_field: str,
    local_field: str,
    parent_collection_name: str,
    parent_model: MongoModel,
    model_out: MongoModel,
) -> MongoModel:
    """
    Update one document in the database with a lookup
    """
    await db[collection_name].replace_one({"_id": ObjectId(lookup_id)}, data.to_mongo())
    return await get_one(
        db,
        collection_name,
        id,
        lookup_id,
        foreign_field,
        local_field,
        parent_collection_name,
        parent_model,
        model_out,
    )


async def update_one(
    db,
    collection_name: str,
    id: str,
    lookup_id: str,
    data,
    foreign_field: str,
    local_field: str,
    parent_collection_name: str,
    parent_model: MongoModel,
    model_out: MongoModel,
) -> MongoModel:
    """
    Update one document in the database with a lookup
    """
    await db[collection_name].update_one(
        {"_id": ObjectId(lookup_id)}, {"$set": data.to_mongo()}
    )
    return await get_one(
        db,
        collection_name,
        id,
        lookup_id,
        foreign_field,
        local_field,
        parent_collection_name,
        parent_model,
        model_out,
    )


async def delete_one(
    db,
    collection_name: str,
    lookup_id: str,
) -> DeletedModelOut:
    """
    Delete one document in the database with a lookup
    """
    await db[collection_name].delete_one({"_id": ObjectId(lookup_id)})
    return DeletedModelOut.from_mongo({"_id": lookup_id})
