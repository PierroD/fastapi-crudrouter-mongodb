import pytest


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
