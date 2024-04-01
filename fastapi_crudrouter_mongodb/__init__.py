from .core import (
    CRUDRouter,
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
    "CRUDLookup",
    "CRUDEmbed",
]

__version__ = "0.1.0"
__author__ = "Pierre DUVEAU"
__credits__ = ["Pierre DUVEAU", "Adam Watkins"]
