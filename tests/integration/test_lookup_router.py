import pytest
from bson import ObjectId


@pytest.mark.asyncio
async def test_lookup_get_all(lookup_client, db):
    child_a = ObjectId()
    child_b = ObjectId()
    parent_id = ObjectId()

    await db["children"].insert_one({"_id": child_a, "name": "Child A"})
    await db["children"].insert_one({"_id": child_b, "name": "Child B"})
    await db["parents"].insert_one(
        {
            "_id": parent_id,
            "name": "Parent",
            "childIds": [child_a, child_b],
        }
    )

    response = await lookup_client.get(f"/parents/{parent_id}/children")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Parent"
    assert len(body["children"]) == 2


@pytest.mark.asyncio
async def test_lookup_get_all_empty(lookup_client, db):
    parent_id = ObjectId()
    await db["parents"].insert_one(
        {
            "_id": parent_id,
            "name": "No child",
            "childIds": [],
        }
    )

    response = await lookup_client.get(f"/parents/{parent_id}/children")
    assert response.status_code == 200
    assert response.json()["children"] == []


@pytest.mark.asyncio
async def test_lookup_pagination_sort(lookup_client, db):
    child_ids = [ObjectId() for _ in range(3)]
    names = ["Charlie", "Alpha", "Bravo"]
    for child_id, name in zip(child_ids, names, strict=False):
        await db["children"].insert_one({"_id": child_id, "name": name})

    parent_id = ObjectId()
    await db["parents"].insert_one(
        {
            "_id": parent_id,
            "name": "Sort parent",
            "childIds": child_ids,
        }
    )

    response = await lookup_client.get(
        f"/parents/{parent_id}/children",
        params={"sort_by": "name", "order_by": "ASC", "limit": 2},
    )

    assert response.status_code == 200
    children = response.json()["children"]
    assert len(children) == 2
    assert [child["name"] for child in children] == ["Alpha", "Bravo"]
