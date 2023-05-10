from typing import Any, Callable, List, Optional, Sequence

from fastapi import HTTPException
from fastapi.params import Depends
from .CRUDRouterFactory import CRUDRouterFactory
from . import CRUDRouterRepository
from .embed.CRUDEmbedRouter import CRUDEmbedRouter
from .lookup.CRUDLookupRouter import CRUDLookupRouter
from ..models.CRUDEmbed import CRUDEmbed
from ..models.CRUDLookup import CRUDLookup
from ..models.mongo_model import MongoModel


class CRUDRouter(CRUDRouterFactory):
    """
    CRUDRouter is a class that extends CRUDRouterFactory and implements the CRUD operations for a given model.

    :param model: The model to be used for the CRUD operations.
    :type model: MongoModel
    :param db: The database to be used for the CRUD operations.
    :type db: Database
    :param collection_name: The name of the collection to be used for the CRUD operations.
    :type collection_name: str
    :param lookups: A list of lookup objects to be used for the CRUD operations.
    :type lookups: List[CRUDLookup]
    :param args: The args to be passed to the CRUDRouterFactory.
    :type args: Any
    :param kwargs: The kwargs to be passed to the CRUDRouterFactory.
    :type kwargs: Any
    """

    def __init__(self,
                 model,
                 db,
                 collection_name,
                 lookups: List[CRUDLookup] = [],
                 disable_get_all=False,
                 disable_get_one=False,
                 disable_create_one=False,
                 disable_replace_one=False,
                 disable_update_one=False,
                 disable_delete_one=False,
                 dependencies_get_all:Optional[Sequence[Depends]] = None,
                 dependencies_get_one:Optional[Sequence[Depends]] = None,
                 dependencies_create_one:Optional[Sequence[Depends]] = None,
                 dependencies_replace_one:Optional[Sequence[Depends]] = None,
                 dependencies_update_one:Optional[Sequence[Depends]] = None,
                 dependencies_delete_one:Optional[Sequence[Depends]] = None,
                 * args, **kwargs) -> None:
        super().__init__(model, db, collection_name, *args, **kwargs)
        self.disable_get_all = disable_get_all
        self.disable_get_one = disable_get_one
        self.disable_create_one = disable_create_one
        self.disable_replace_one = disable_replace_one
        self.disable_update_one = disable_update_one
        self.disable_delete_one = disable_delete_one
        self.dependencies_get_all = dependencies_get_all
        self.dependencies_get_one = dependencies_get_one
        self.dependencies_create_one = dependencies_create_one
        self.dependencies_replace_one = dependencies_replace_one
        self.dependencies_update_one = dependencies_update_one
        self.dependencies_delete_one = dependencies_delete_one
        self._register_routes()
        try:
            for lookup in lookups:
                CRUDLookupRouter(self, lookup, *args, **kwargs)
            for key, value in self.model.__fields__.items():
                try:
                    if (key in self.model.__fields__ and issubclass(self.model.__fields__[key].type_, MongoModel)):
                        embed_model = CRUDEmbed(
                            self.model.__fields__[key].type_, key)
                        CRUDEmbedRouter(self, embed_model, *args, **kwargs)
                except Exception as e:
                    continue

        except Exception as e:
            print(e)

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route() -> list:
            response = await CRUDRouterRepository.get_all(self.db, self.model, self.collection_name)
            if (not len(response)):
                raise HTTPException(404, "Empty collection")
            return response
        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str) -> self.model:
            response = await CRUDRouterRepository.get_one(self.db, self.model, self.collection_name, id)
            if (response is None):
                raise HTTPException(404, "Document not found")
            return response
        return route

    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(data: self.model) -> self.model:
            response = await CRUDRouterRepository.create_one(self.db, self.model, self.collection_name, data)
            if (response is None):
                raise HTTPException(422, "Document not created")
            return response
        return route

    def _replace_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, data: self.model) -> self.model:
            response = await CRUDRouterRepository.replace_one(self.db, self.model, self.collection_name, id, data)
            if (response is None):
                raise HTTPException(422, "Document not replaced")
            return response
        return route

    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, data: self.model) -> self.model:
            response = await CRUDRouterRepository.update_one(self.db, self.model, self.collection_name, id, data)
            if (response is None):
                raise HTTPException(422, "Document not updated")
            return response
        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str) -> self.model:
            response = await CRUDRouterRepository.delete_one(self.db, self.collection_name, id)
            if (response is None):
                raise HTTPException(422, "Document not deleted")
            return response
        return route

    def _register_routes(self):
        if (not self.disable_get_all):
            self._add_api_route(
                "/",
                self._get_all(),
                response_model=List[self.model],
                dependencies=self.dependencies_get_all,
                methods=["GET"],
                summary=f"Get All {self.model.__name__} from the collection",
                description=f"Get All {self.model.__name__} from the collection")
        if (not self.disable_get_one):
            self._add_api_route(
                "/{id}",
                self._get_one(),
                response_model=self.model,
                dependencies=self.dependencies_get_one,
                methods=["GET"],
                summary=f"Get One {self.model.__name__} by {{id}} from the collection",
                description=f"Get One {self.model.__name__} by {{id}} from the collection",
            )
        if (not self.disable_create_one):
            self._add_api_route(
                "/",
                self._create_one(),
                response_model=self.model,
                dependencies=self.dependencies_create_one,
                methods=["POST"],
                summary=f"Create One {self.model.__name__} in the collection",
                description=f"Create One {self.model.__name__} in the collection")
        if (not self.disable_update_one):
            self._add_api_route(
                "/{id}",
                self._update_one(),
                response_model=self.model,
                dependencies=self.dependencies_update_one,
                methods=["PATCH"],
                summary=f"Update One {self.model.__name__} by {{id}} in the collection",
                description=f"Update One {self.model.__name__} by {{id}} in the collection",
            )
        if (not self.disable_replace_one):
            self._add_api_route(
                "/{id}",
                self._replace_one(),
                response_model=self.model,
                dependencies=self.dependencies_replace_one,
                methods=["PUT"],
                summary=f"Replace One {self.model.__name__} by {{id}} in the collection",
                description=f"Replace One {self.model.__name__} by {{id}} in the collection",
            )
        if (not self.disable_delete_one):
            self._add_api_route(
                "/{id}",
                self._delete_one(),
                response_model=self.model,
                dependencies=self.dependencies_delete_one,
                methods=["DELETE"],
                summary=f"Delete One {self.model.__name__} by {{id}} from the collection",
                description=f"Delete One {self.model.__name__} by {{id}} from the collection",
            )
