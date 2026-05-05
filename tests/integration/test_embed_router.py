import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from fastapi_crudrouter_mongodb import CRUDEmbed, CRUDRouter, MongoModel


@pytest.mark.asyncio
async def test_embed_get_all_empty(embed_client):
    created_article = await embed_client.post("/articles", json={"title": "A"})
    article_id = created_article.json()["id"]

    response = await embed_client.get(f"/articles/{article_id}/tags")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_embed_create_one(embed_client):
    created_article = await embed_client.post("/articles", json={"title": "Create"})
    article_id = created_article.json()["id"]

    response = await embed_client.post(
        f"/articles/{article_id}/tags",
        json={"name": "tag-1"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "tag-1"


@pytest.mark.asyncio
async def test_embed_get_one(embed_client):
    created_article = await embed_client.post("/articles", json={"title": "GetOne"})
    article_id = created_article.json()["id"]
    created_tag = await embed_client.post(
        f"/articles/{article_id}/tags",
        json={"name": "tag-one"},
    )
    tag_id = created_tag.json()["id"]

    response = await embed_client.get(f"/articles/{article_id}/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "tag-one"


@pytest.mark.asyncio
async def test_embed_delete_one(embed_client):
    created_article = await embed_client.post("/articles", json={"title": "Delete"})
    article_id = created_article.json()["id"]
    created_tag = await embed_client.post(
        f"/articles/{article_id}/tags",
        json={"name": "tag-del"},
    )
    tag_id = created_tag.json()["id"]

    response = await embed_client.delete(f"/articles/{article_id}/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json()["id"] == tag_id


@pytest.mark.asyncio
async def test_embed_get_all_pagination(embed_client):
    created_article = await embed_client.post("/articles", json={"title": "Paginate"})
    article_id = created_article.json()["id"]

    for i in range(5):
        await embed_client.post(
            f"/articles/{article_id}/tags",
            json={"name": f"tag-{i}"},
        )

    response = await embed_client.get(
        f"/articles/{article_id}/tags",
        params={"limit": 2},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# Custom embed identifier_field
# ---------------------------------------------------------------------------


class Track(MongoModel):
    isrc: str
    title: str
    files: list = []


class TrackFile(MongoModel):
    file_type: str
    url: str


@pytest_asyncio.fixture
async def track_client():
    client = AsyncMongoMockClient()
    db = client["testdb"]
    app = FastAPI()
    router = CRUDRouter(
        model=Track,
        db=db,
        collection_name="tracks",
        prefix="/tracks",
        identifier_field="isrc",
        embeds=[
            CRUDEmbed(
                model=TrackFile,
                embed_name="files",
                identifier_field="file_type",
            )
        ],
    )
    app.include_router(router)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_embed_custom_identifier_crud(track_client):
    # create parent track using its string isrc identifier
    created = await track_client.post(
        "/tracks", json={"isrc": "FR7O52600080", "title": "Test Track"}
    )
    assert created.status_code == 200

    # create embedded file
    created_file = await track_client.post(
        "/tracks/FR7O52600080/files",
        json={"file_type": "mp3", "url": "https://example.com/track.mp3"},
    )
    assert created_file.status_code == 200
    assert (
        created_file.json().get("file_type") == "mp3"
        or created_file.json().get("fileType") == "mp3"
    )

    # get all embedded files
    all_files = await track_client.get("/tracks/FR7O52600080/files")
    assert all_files.status_code == 200
    assert len(all_files.json()) == 1

    # get one by custom identifier
    one_file = await track_client.get("/tracks/FR7O52600080/files/mp3")
    assert one_file.status_code == 200
    assert one_file.json()["url"] == "https://example.com/track.mp3"

    # delete by custom identifier
    deleted = await track_client.delete("/tracks/FR7O52600080/files/mp3")
    assert deleted.status_code == 200

    # confirm gone
    after_delete = await track_client.get("/tracks/FR7O52600080/files")
    assert after_delete.status_code == 200
    assert after_delete.json() == []
