from .core import (
    CRUDRouter,
    CRUDRouterService,
    MongoObjectId,
    MongoModel,
    DeletedModelOut,
    CRUDLookup,
    CRUDEmbed,
)
from bson import ObjectId

__all__ = [
    "ObjectId",
    "MongoObjectId",
    "MongoModel",
    "DeletedModelOut",
    "CRUDRouter",
    "CRUDRouterService",
    "CRUDLookup",
    "CRUDEmbed",
]

__version__ = "0.1.4"
__author__ = "Pierre DUVEAU"
__credits__ = ["Pierre DUVEAU", "Adam Watkins"]
