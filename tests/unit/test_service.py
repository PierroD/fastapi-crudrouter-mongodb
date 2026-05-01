import pytest
from bson import ObjectId
from fastapi import HTTPException

from fastapi_crudrouter_mongodb import CRUDPopulate
from tests.conftest import Artist, Producer, TestItem, Track


@pytest.mark.asyncio
async def test_find_all_returns_list(service):
    await service.create_one(TestItem(id=ObjectId(), name="A"))

    result = await service.find_all()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_find_all_empty(service):
    result = await service.find_all()
    assert result == []


@pytest.mark.asyncio
async def test_find_one_success(service):
    created = await service.create_one(TestItem(id=ObjectId(), name="One"))

    result = await service.find_one(str(created.id))
    assert result.id == created.id


@pytest.mark.asyncio
async def test_find_one_not_found_raises_http(service):
    with pytest.raises(HTTPException) as exc_info:
        await service.find_one(str(ObjectId()))

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_one_success(service):
    result = await service.create_one(TestItem(id=ObjectId(), name="Create"))
    assert result.name == "Create"


@pytest.mark.asyncio
async def test_create_one_duplicate(service):
    shared_id = ObjectId()
    await service.create_one(TestItem(id=shared_id, name="First"))

    with pytest.raises(HTTPException) as exc_info:
        await service.create_one(TestItem(id=shared_id, name="Second"))

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_replace_one_success(service):
    created = await service.create_one(TestItem(id=ObjectId(), name="Before"))

    replaced = await service.replace_one(
        str(created.id),
        TestItem(id=created.id, name="After"),
    )

    assert replaced.name == "After"


@pytest.mark.asyncio
async def test_replace_one_not_found(service):
    with pytest.raises(HTTPException) as exc_info:
        await service.replace_one(
            str(ObjectId()), TestItem(id=ObjectId(), name="Ghost")
        )

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_update_one_success(service):
    created = await service.create_one(
        TestItem(id=ObjectId(), name="Before", status="x")
    )

    updated = await service.update_one(
        str(created.id),
        TestItem(id=created.id, name="After", status="y"),
    )

    assert updated.name == "After"
    assert updated.status == "y"


@pytest.mark.asyncio
async def test_delete_one_success(service):
    created = await service.create_one(TestItem(id=ObjectId(), name="Delete"))

    response = await service.delete_one(str(created.id))
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_one_not_found(service):
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_one(str(ObjectId()))

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_find_all_with_model_out(service_with_model_out):
    await service_with_model_out.create_one(
        TestItem(id=ObjectId(), name="Out", status="active")
    )

    results = await service_with_model_out.find_all()
    assert len(results) == 1
    assert hasattr(results[0], "name")
    assert not hasattr(results[0], "value")


@pytest.mark.asyncio
async def test_find_one_with_model_out(service_with_model_out):
    item_id = ObjectId()
    await service_with_model_out.db["items"].insert_one(
        TestItem(id=item_id, name="Out One", status="active", value=99).to_mongo()
    )

    result = await service_with_model_out.find_one(str(item_id))
    assert hasattr(result, "name")
    assert not hasattr(result, "value")


@pytest.mark.asyncio
async def test_find_all_with_skip_limit(service):
    for i in range(5):
        await service.create_one(TestItem(id=ObjectId(), name=f"Item {i}", value=i))

    results = await service.find_all(skip=1, limit=2)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_find_all_with_filters(service):
    await service.create_one(TestItem(id=ObjectId(), name="A", status="active"))
    await service.create_one(TestItem(id=ObjectId(), name="B", status="inactive"))

    results = await service.find_all(filters={"status": "active"})
    assert len(results) == 1
    assert results[0].status == "active"


@pytest.mark.asyncio
async def test_find_all_with_populates(db):
    artist_id = ObjectId()
    producer_id = ObjectId()
    track_id = ObjectId()

    await db["artists"].insert_one({"_id": artist_id, "name": "Artist 1"})
    await db["producers"].insert_one({"_id": producer_id, "name": "Producer 1"})
    await db["tracks"].insert_one(
        {
            "_id": track_id,
            "title": "Track 1",
            "artistIds": [artist_id],
            "producerIds": [producer_id],
        }
    )

    from fastapi_crudrouter_mongodb import CRUDService

    track_service = CRUDService(model=Track, db=db, collection_name="tracks")
    results = await track_service.find_all(
        populates=[
            CRUDPopulate(field="artist_ids", collection="artists", model=Artist),
            CRUDPopulate(field="producer_ids", collection="producers", model=Producer),
        ]
    )

    assert len(results) == 1
    assert results[0]["artistIds"][0]["name"] == "Artist 1"
    assert results[0]["producerIds"][0]["name"] == "Producer 1"


@pytest.mark.asyncio
async def test_find_one_with_populates(db):
    artist_id = ObjectId()
    track_id = ObjectId()

    await db["artists"].insert_one({"_id": artist_id, "name": "Artist X"})
    await db["tracks"].insert_one(
        {
            "_id": track_id,
            "title": "Track X",
            "artistIds": [artist_id],
            "producerIds": [],
        }
    )

    from fastapi_crudrouter_mongodb import CRUDService

    track_service = CRUDService(model=Track, db=db, collection_name="tracks")
    result = await track_service.find_one(
        str(track_id),
        populates=[
            CRUDPopulate(field="artist_ids", collection="artists", model=Artist)
        ],
    )

    assert result["artistIds"][0]["name"] == "Artist X"


@pytest.mark.asyncio
async def test_find_all_no_populates(db):
    artist_id = ObjectId()
    await db["tracks"].insert_one(
        {
            "_id": ObjectId(),
            "title": "Track Raw",
            "artistIds": [artist_id],
            "producerIds": [],
        }
    )

    from fastapi_crudrouter_mongodb import CRUDService

    track_service = CRUDService(model=Track, db=db, collection_name="tracks")
    results = await track_service.find_all(populates=None)

    assert len(results) == 1
    assert str(results[0].artist_ids[0]) == str(artist_id)
