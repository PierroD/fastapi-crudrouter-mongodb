from .core import (
    CRUDRouter,
    CRUDService,
    CRUDRepository,
    MongoObjectId,
    ObjectIdType,
    MongoModel,
    CamelModel,
    CRUDLookup,
    CRUDEmbed,
    CRUDPopulate,
)
from bson import ObjectId

__all__ = [
    "ObjectId",
    "MongoObjectId",
    "ObjectIdType",
    "MongoModel",
    "CamelModel",
    "CRUDRouter",
    "CRUDService",
    "CRUDRepository",
    "CRUDLookup",
    "CRUDEmbed",
    "CRUDPopulate",
]

__version__ = "1.0.0"
__author__ = "Pierre DUVEAU"
__credits__ = ["Pierre DUVEAU", "Adam Watkins"]
