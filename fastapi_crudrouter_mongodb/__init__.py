from .core import (
    CRUDRouter,
    CRUDService,
    MongoObjectId,
    MongoModel,
    CamelModel,
    CRUDLookup,
    CRUDEmbed,
)
from bson import ObjectId

__all__ = [
    "ObjectId",
    "MongoObjectId",
    "MongoModel",
    "CamelModel",
    "CRUDRouter",
    "CRUDService",
    "CRUDLookup",
    "CRUDEmbed",
]

__version__ = "0.1.4"
__author__ = "Pierre DUVEAU"
__credits__ = ["Pierre DUVEAU", "Adam Watkins"]
