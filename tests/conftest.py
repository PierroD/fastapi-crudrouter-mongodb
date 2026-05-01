from typing import Annotated

import pytest_asyncio
from bson import ObjectId
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from fastapi_crudrouter_mongodb import (
    CRUDEmbed,
    CRUDLookup,
    CRUDPopulate,
    CRUDRepository,
    CRUDRouter,
    CRUDService,
    CamelModel,
    MongoModel,
    MongoObjectId,
)

ObjectIdType = Annotated[ObjectId, MongoObjectId]


class TestItem(MongoModel):
    __test__ = False
    id: ObjectIdType | None = None
    name: str
    status: str | None = None
    value: int | None = None


class TestItemOut(CamelModel):
    name: str
    status: str | None = None


class Tag(MongoModel):
    id: ObjectIdType | None = None
    name: str


class Article(MongoModel):
    id: ObjectIdType | None = None
    title: str
    tags: list[Tag] = []


class ChildRef(MongoModel):
    id: ObjectIdType | None = None
    name: str


class ParentWithLookup(MongoModel):
    id: ObjectIdType | None = None
    name: str
    child_ids: list[ObjectIdType] = []
    children: list[dict] = []


class ParentWithLookupOut(CamelModel):
    id: str | None = None
    name: str
    child_ids: list[str] = []
    children: list[dict] = []


class Artist(MongoModel):
    id: ObjectIdType | None = None
    name: str


class Producer(MongoModel):
    id: ObjectIdType | None = None
    name: str


class ArtistPopulateOut(CamelModel):
    name: str


class ProducerPopulateOut(CamelModel):
    id: str
    name: str


class Track(MongoModel):
    id: ObjectIdType | None = None
    title: str
    artist_ids: list[ObjectIdType] = []
    producer_ids: list[ObjectIdType] = []


class TrackOut(CamelModel):
    id: str | None = None
    title: str
    artist_ids: list[ArtistPopulateOut] = []
    producer_ids: list[ProducerPopulateOut] = []


class TrackParentModelCompatibleOut(CamelModel):
    id: str | None = None
    title: str
    artist_ids: list[ArtistPopulateOut] = []
    producer_ids: list[Producer] = []


class CircularTrack(MongoModel):
    id: ObjectIdType | None = None
    title: str
    related_ids: list[ObjectIdType] = []


@pytest_asyncio.fixture
async def db():
    client = AsyncMongoMockClient()
    yield client["testdb"]


@pytest_asyncio.fixture
async def repository(db):
    return CRUDRepository(model=TestItem, db=db, collection_name="items")


@pytest_asyncio.fixture
async def populated_repository(repository):
    for i in range(5):
        item = TestItem(
            id=ObjectId(),
            name=f"Item {i}",
            status="active" if i % 2 == 0 else "inactive",
            value=i,
        )
        await repository.create_one(item)
    return repository


@pytest_asyncio.fixture
async def service(db):
    return CRUDService(model=TestItem, db=db, collection_name="items")


@pytest_asyncio.fixture
async def service_with_model_out(db):
    return CRUDService(
        model=TestItem,
        db=db,
        collection_name="items",
        model_out=TestItemOut,
    )


@pytest_asyncio.fixture
async def app(db):
    application = FastAPI()
    router = CRUDRouter(
        model=TestItem,
        db=db,
        collection_name="items",
        prefix="/items",
        tags=["items"],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def app_with_embed(db):
    application = FastAPI()
    router = CRUDRouter(
        model=Article,
        db=db,
        collection_name="articles",
        prefix="/articles",
        tags=["articles"],
        embeds=[CRUDEmbed(model=Tag, embed_name="tags")],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def embed_client(app_with_embed):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_embed),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def app_with_lookup(db):
    application = FastAPI()
    router = CRUDRouter(
        model=ParentWithLookup,
        db=db,
        collection_name="parents",
        prefix="/parents",
        tags=["parents"],
        lookups=[
            CRUDLookup(
                model=ChildRef,
                model_out=ParentWithLookupOut,
                collection_name="children",
                prefix="children",
                local_field="childIds",
                foreign_field="_id",
            )
        ],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def lookup_client(app_with_lookup):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_lookup),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def app_with_populate(db):
    application = FastAPI()
    router = CRUDRouter(
        model=Track,
        db=db,
        collection_name="tracks",
        prefix="/tracks",
        tags=["tracks"],
        populates=[
            CRUDPopulate(
                field="artist_ids",
                collection="artists",
                model=Artist,
                model_out=ArtistPopulateOut,
            ),
            CRUDPopulate(field="producer_ids", collection="producers", model=Producer),
        ],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def populate_client(app_with_populate):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_populate),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def app_with_populate_model_out(db):
    application = FastAPI()
    router = CRUDRouter(
        model=Track,
        model_out=TrackOut,
        db=db,
        collection_name="tracks",
        prefix="/tracks-out",
        tags=["tracks-out"],
        populates=[
            CRUDPopulate(
                field="artist_ids",
                collection="artists",
                model=Artist,
                model_out=ArtistPopulateOut,
            ),
            CRUDPopulate(
                field="producer_ids",
                collection="producers",
                model=Producer,
                model_out=ProducerPopulateOut,
            ),
        ],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def populate_model_out_client(app_with_populate_model_out):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_populate_model_out),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def app_with_populate_parent_model_schema(db):
    application = FastAPI()
    router = CRUDRouter(
        model=Track,
        model_out=TrackParentModelCompatibleOut,
        db=db,
        collection_name="tracks",
        prefix="/tracks-parent-model",
        tags=["tracks-parent-model"],
        populates=[
            CRUDPopulate(
                field="artist_ids",
                collection="artists",
                model=Artist,
                model_out=ArtistPopulateOut,
            ),
            CRUDPopulate(
                field="producer_ids",
                collection="producers",
                model=Producer,
                model_out=ProducerPopulateOut,
            ),
        ],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def populate_parent_model_schema_client(app_with_populate_parent_model_schema):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_populate_parent_model_schema),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def app_with_circular_populate(db):
    application = FastAPI()
    router = CRUDRouter(
        model=CircularTrack,
        db=db,
        collection_name="circular_tracks",
        prefix="/circular-tracks",
        populates=[
            CRUDPopulate(
                field="related_ids",
                collection="circular_tracks",
                model=CircularTrack,
            )
        ],
    )
    application.include_router(router)
    return application


@pytest_asyncio.fixture
async def circular_populate_client(app_with_circular_populate):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_circular_populate),
        base_url="http://test",
        follow_redirects=True,
    ) as async_client:
        yield async_client
