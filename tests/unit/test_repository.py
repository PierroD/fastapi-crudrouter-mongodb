import pytest
from bson import ObjectId

from fastapi_crudrouter_mongodb import CRUDPopulate
from tests.conftest import Artist, TestItem, Track


@pytest.mark.asyncio
async def test_find_all_empty(repository):
    result = await repository.find_all()
    assert result == []


@pytest.mark.asyncio
async def test_find_all_returns_all(populated_repository):
    result = await populated_repository.find_all()
    assert len(result) == 5


@pytest.mark.asyncio
async def test_find_one_exists(repository):
    item = TestItem(id=ObjectId(), name="One")
    created = await repository.create_one(item)

    found = await repository.find_one(str(created.id))
    assert found is not None
    assert found.name == "One"


@pytest.mark.asyncio
async def test_find_one_not_found(repository):
    found = await repository.find_one(str(ObjectId()))
    assert found is None


@pytest.mark.asyncio
async def test_create_one_success(repository):
    item = TestItem(id=ObjectId(), name="Create")

    created = await repository.create_one(item)
    assert created is not None
    assert created.name == "Create"


@pytest.mark.asyncio
async def test_create_one_duplicate(repository):
    shared_id = ObjectId()
    first = TestItem(id=shared_id, name="First")
    second = TestItem(id=shared_id, name="Second")

    assert await repository.create_one(first) is not None
    assert await repository.create_one(second) is None


@pytest.mark.asyncio
async def test_replace_one_success(repository):
    item = TestItem(id=ObjectId(), name="Before", status="active")
    created = await repository.create_one(item)

    updated = await repository.replace_one(
        str(created.id),
        TestItem(id=created.id, name="After", status="inactive"),
    )

    assert updated is not None
    assert updated.name == "After"
    assert updated.status == "inactive"


@pytest.mark.asyncio
async def test_replace_one_not_found(repository):
    replaced = await repository.replace_one(
        str(ObjectId()),
        TestItem(id=ObjectId(), name="Ghost"),
    )
    assert replaced is None


@pytest.mark.asyncio
async def test_delete_one_success(repository):
    item = TestItem(id=ObjectId(), name="Delete")
    created = await repository.create_one(item)

    deleted = await repository.delete_one(str(created.id))
    assert deleted is not None
    assert str(deleted.id) == str(created.id)


@pytest.mark.asyncio
async def test_delete_one_not_found(repository):
    deleted = await repository.delete_one(str(ObjectId()))
    assert deleted is None


@pytest.mark.asyncio
async def test_find_all_skip(populated_repository):
    result = await populated_repository.find_all(skip=2)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_find_all_limit(populated_repository):
    result = await populated_repository.find_all(limit=2)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_find_all_sort_asc(populated_repository):
    result = await populated_repository.find_all(sort_by="name", order_by="ASC")
    names = [item.name for item in result]
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_find_all_sort_desc(populated_repository):
    result = await populated_repository.find_all(sort_by="name", order_by="DESC")
    names = [item.name for item in result]
    assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_find_all_filters(populated_repository):
    result = await populated_repository.find_all(filters={"status": "active"})
    assert len(result) == 3
    assert all(item.status == "active" for item in result)


@pytest.mark.asyncio
async def test_get_all_deprecated(populated_repository):
    find_all_result = await populated_repository.find_all()
    get_all_result = await populated_repository.get_all()

    assert len(get_all_result) == len(find_all_result)


@pytest.mark.asyncio
async def test_get_one_deprecated(repository):
    item = TestItem(id=ObjectId(), name="Legacy")
    created = await repository.create_one(item)

    direct = await repository.find_one(str(created.id))
    legacy = await repository.get_one(str(created.id))

    assert legacy is not None
    assert direct is not None
    assert legacy.id == direct.id


@pytest.mark.asyncio
async def test_resolve_populate_batch(repository, db):
    artist_id = ObjectId()
    await db["artists"].insert_one({"_id": artist_id, "name": "Artist A"})

    track = Track(
        id=ObjectId(), title="Track 1", artist_ids=[artist_id], producer_ids=[]
    )
    created_track = await db["items"].insert_one(track.to_mongo())
    docs = [
        Track.from_mongo(await db["items"].find_one({"_id": created_track.inserted_id}))
    ]

    populated = await repository.resolve_populate(
        docs,
        [CRUDPopulate(field="artist_ids", collection="artists", model=Artist)],
    )

    assert populated
    assert populated[0].artist_ids
    assert populated[0].artist_ids[0].name == "Artist A"
