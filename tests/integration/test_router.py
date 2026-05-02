import json

import pytest
from bson import ObjectId
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from fastapi_crudrouter_mongodb import CRUDRouter
from tests.conftest import TestItem


@pytest.mark.asyncio
async def test_get_all_empty(client):
    response = await client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_one(client):
    response = await client.post("/items", json={"name": "A", "status": "active"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "A"
    assert "id" in body


@pytest.mark.asyncio
async def test_get_one(client):
    created = await client.post("/items", json={"name": "B"})
    item_id = created.json()["id"]

    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "B"


@pytest.mark.asyncio
async def test_get_one_not_found(client):
    response = await client.get(f"/items/{ObjectId()}")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_replace_one(client):
    created = await client.post("/items", json={"name": "Before", "status": "active"})
    item_id = created.json()["id"]

    response = await client.put(
        f"/items/{item_id}",
        json={"id": item_id, "name": "After", "status": "inactive"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "After"


@pytest.mark.asyncio
async def test_update_one(client):
    created = await client.post("/items", json={"name": "Before", "status": "active"})
    item_id = created.json()["id"]

    response = await client.patch(
        f"/items/{item_id}",
        json={"id": item_id, "name": "After", "status": "inactive"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


@pytest.mark.asyncio
async def test_delete_one(client):
    created = await client.post("/items", json={"name": "Delete"})
    item_id = created.json()["id"]

    response = await client.delete(f"/items/{item_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_disable_create_one(db):
    app = FastAPI()
    router = CRUDRouter(
        model=TestItem,
        db=db,
        collection_name="items",
        prefix="/items",
        disable_create_one=True,
    )
    app.include_router(router)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        response = await async_client.post("/items", json={"name": "Blocked"})

    assert response.status_code in (404, 405)


@pytest.mark.asyncio
async def test_disable_get_all(db):
    app = FastAPI()
    router = CRUDRouter(
        model=TestItem,
        db=db,
        collection_name="items",
        prefix="/items",
        disable_get_all=True,
    )
    app.include_router(router)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        response = await async_client.get("/items")

    assert response.status_code in (404, 405)


@pytest.mark.asyncio
async def test_identifier_field_in_routes(db):
    class UserByEmail(TestItem):
        email: str

    app = FastAPI()
    router = CRUDRouter(
        model=UserByEmail,
        db=db,
        collection_name="users",
        prefix="/users",
        identifier_field="email",
    )
    app.include_router(router)

    paths = app.openapi()["paths"].keys()
    assert "/users/{email}" in paths


@pytest.mark.asyncio
async def test_identifier_field_email_path_runtime(db):
    class UserByEmail(TestItem):
        email: str

    app = FastAPI()
    router = CRUDRouter(
        model=UserByEmail,
        db=db,
        collection_name="users",
        prefix="/users",
        identifier_field="email",
    )
    app.include_router(router)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        created = await async_client.post(
            "/users",
            json={"name": "Alice", "email": "alice@example.com"},
        )
        assert created.status_code == 200

        response = await async_client.get("/users/alice@example.com")

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_get_all_with_limit(client):
    for i in range(5):
        await client.post("/items", json={"name": f"Item {i}"})

    response = await client.get("/items", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_all_with_skip(client):
    for i in range(5):
        await client.post("/items", json={"name": f"Skip {i}"})

    response = await client.get("/items", params={"skip": 3})
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_all_with_filters(client):
    await client.post("/items", json={"name": "A", "status": "active"})
    await client.post("/items", json={"name": "B", "status": "inactive"})

    response = await client.get(
        "/items", params={"filters": json.dumps({"status": "active"})}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "active"


@pytest.mark.asyncio
async def test_get_all_invalid_filters(client):
    response = await client.get("/items", params={"filters": "INVALID_JSON"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid JSON in filters parameter"


@pytest.mark.asyncio
async def test_get_all_with_sort(client):
    await client.post("/items", json={"name": "A"})
    await client.post("/items", json={"name": "C"})
    await client.post("/items", json={"name": "B"})

    response = await client.get(
        "/items", params={"sort_by": "name", "order_by": "DESC"}
    )
    assert response.status_code == 200
    names = [row["name"] for row in response.json()]
    assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_filter_dependency(client, db):
    def active_filter_dependency():
        return {"status": "active"}

    app = FastAPI()
    router = CRUDRouter(
        model=TestItem,
        db=db,
        collection_name="items",
        prefix="/items-filtered",
        filter_dependency=active_filter_dependency,
    )
    app.include_router(router)

    seed_router = CRUDRouter(
        model=TestItem,
        db=db,
        collection_name="items",
        prefix="/items",
    )
    app.include_router(seed_router)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        await async_client.post("/items", json={"name": "A", "status": "active"})
        await async_client.post("/items", json={"name": "B", "status": "inactive"})
        response = await async_client.get("/items-filtered")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "active"
