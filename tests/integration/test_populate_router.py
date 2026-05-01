import pytest
from bson import ObjectId


@pytest.mark.asyncio
async def test_populate_single_field(populate_client, db):
    artist_id = ObjectId()
    await db["artists"].insert_one({"_id": artist_id, "name": "Artist 1"})
    await db["tracks"].insert_one(
        {
            "_id": ObjectId(),
            "title": "Track 1",
            "artistIds": [artist_id],
            "producerIds": [],
        }
    )

    response = await populate_client.get("/tracks")
    assert response.status_code == 200
    tracks = response.json()
    assert len(tracks) == 1
    assert tracks[0]["artistIds"][0]["name"] == "Artist 1"
    assert "id" not in tracks[0]["artistIds"][0]


@pytest.mark.asyncio
async def test_populate_multi_field(populate_client, db):
    artist_id = ObjectId()
    producer_id = ObjectId()
    await db["artists"].insert_one({"_id": artist_id, "name": "Artist Multi"})
    await db["producers"].insert_one({"_id": producer_id, "name": "Producer Multi"})
    await db["tracks"].insert_one(
        {
            "_id": ObjectId(),
            "title": "Track Multi",
            "artistIds": [artist_id],
            "producerIds": [producer_id],
        }
    )

    response = await populate_client.get("/tracks")
    assert response.status_code == 200
    track = response.json()[0]
    assert track["artistIds"][0]["name"] == "Artist Multi"
    assert "id" not in track["artistIds"][0]
    assert track["producerIds"][0]["name"] == "Producer Multi"
    assert "id" in track["producerIds"][0]


@pytest.mark.asyncio
async def test_populate_missing_reference(populate_client, db):
    await db["tracks"].insert_one(
        {
            "_id": ObjectId(),
            "title": "Track Missing",
            "artistIds": [ObjectId()],
            "producerIds": [],
        }
    )

    response = await populate_client.get("/tracks")
    assert response.status_code == 200
    track = response.json()[0]
    assert track["artistIds"] == []


@pytest.mark.asyncio
async def test_populate_get_one(populate_client, db):
    artist_id = ObjectId()
    track_id = ObjectId()
    await db["artists"].insert_one({"_id": artist_id, "name": "Artist One"})
    await db["tracks"].insert_one(
        {
            "_id": track_id,
            "title": "Track One",
            "artistIds": [artist_id],
            "producerIds": [],
        }
    )

    response = await populate_client.get(f"/tracks/{track_id}")
    assert response.status_code == 200
    assert response.json()["artistIds"][0]["name"] == "Artist One"
    assert "id" not in response.json()["artistIds"][0]


@pytest.mark.asyncio
async def test_populate_with_router_model_out(populate_model_out_client, db):
    artist_id = ObjectId()
    producer_id = ObjectId()
    track_id = ObjectId()
    await db["artists"].insert_one({"_id": artist_id, "name": "Artist Out"})
    await db["producers"].insert_one({"_id": producer_id, "name": "Producer Out"})
    await db["tracks"].insert_one(
        {
            "_id": track_id,
            "title": "Track Out",
            "artistIds": [artist_id],
            "producerIds": [producer_id],
        }
    )

    response = await populate_model_out_client.get("/tracks-out")
    assert response.status_code == 200
    payload = response.json()[0]
    assert payload["title"] == "Track Out"
    assert payload["artistIds"] == [{"name": "Artist Out"}]
    assert payload["producerIds"] == [{"id": str(producer_id), "name": "Producer Out"}]


@pytest.mark.asyncio
async def test_populate_with_parent_schema_model_fields(
    populate_parent_model_schema_client,
    db,
):
    artist_id = ObjectId()
    producer_id = ObjectId()
    track_id = ObjectId()
    await db["artists"].insert_one({"_id": artist_id, "name": "Artist Parent"})
    await db["producers"].insert_one({"_id": producer_id, "name": "Producer Parent"})
    await db["tracks"].insert_one(
        {
            "_id": track_id,
            "title": "Track Parent",
            "artistIds": [artist_id],
            "producerIds": [producer_id],
        }
    )

    response = await populate_parent_model_schema_client.get("/tracks-parent-model")
    assert response.status_code == 200
    payload = response.json()[0]
    assert payload["artistIds"] == [{"name": "Artist Parent"}]
    assert payload["producerIds"] == [
        {"id": str(producer_id), "name": "Producer Parent"}
    ]


@pytest.mark.asyncio
async def test_populate_circular_reference(circular_populate_client, db):
    seed_id = ObjectId()
    await db["circular_tracks"].insert_one(
        {
            "_id": seed_id,
            "title": "Circular",
            "relatedIds": [seed_id],
        }
    )

    response = await circular_populate_client.get("/circular-tracks")
    assert response.status_code >= 400
