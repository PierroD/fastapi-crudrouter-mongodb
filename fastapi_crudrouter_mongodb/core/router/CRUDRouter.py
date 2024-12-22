from typing import Any, Callable, Sequence
from pydantic import BaseModel
from fastapi.params import Depends
from .CRUDRouterFactory import CRUDRouterFactory
from .CRUDRouterService import CRUDRouterService
from .embed.CRUDEmbedRouter import CRUDEmbedRouter
from .lookup.CRUDLookupRouter import CRUDLookupRouter
from ..models.CRUDEmbed import CRUDEmbed
from ..models.CRUDLookup import CRUDLookup
from ..models.deleted_mongo_model import DeletedModelOut


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

    def __init__(
        self,
        model,
        db,
        collection_name,
        model_out: BaseModel | None = None,
        lookups: list[CRUDLookup] | None = None,
        embeds: list[CRUDEmbed] | None = None,
        disable_get_all=False,
        disable_get_one=False,
        disable_create_one=False,
        disable_replace_one=False,
        disable_update_one=False,
        disable_delete_one=False,
        dependencies_get_all: Sequence[Depends] | None = None,
        dependencies_get_one: Sequence[Depends] | None = None,
        dependencies_create_one: Sequence[Depends] | None = None,
        dependencies_replace_one: Sequence[Depends] | None = None,
        dependencies_update_one: Sequence[Depends] | None = None,
        dependencies_delete_one: Sequence[Depends] | None = None,
        *args,
        **kwargs,
    ) -> None:
        if lookups is None:
            lookups = []
        super().__init__(model, db, collection_name, *args, **kwargs)
        self.service = CRUDRouterService(model, db, collection_name, model_out)
        self.model_out = model if model_out is None else model_out
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
            if lookups is not None:
                for lookup in lookups:
                    CRUDLookupRouter(self, lookup, *args, **kwargs)
            if embeds is not None:
                for embed in embeds:
                    CRUDEmbedRouter(self, embed, *args, **kwargs)
        except Exception as e:
            print(e)

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route() -> list[self.model]:
            return await self.service.get_all()

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str) -> self.model:
            return await self.service.get_one(id)

        return route

    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(data: self.model) -> self.model:
            return await self.service.create_one(data)

        return route

    def _replace_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, data: self.model) -> self.model:
            return await self.service.replace_one(id, data)

        return route

    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, data: self.model) -> self.model:
            return await self.service.update_one(id, data)

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str) -> DeletedModelOut:
            return await self.service.delete_one(id)

        return route

    def _register_routes(self) -> None:
        """
        Register the routes for the CRUDRouter.

        :return: None
        :rtype: None
        """
        if not self.disable_get_all:
            self._add_api_route(
                "/",
                self._get_all(),
                response_model=list[self.model_out],
                dependencies=self.dependencies_get_all,
                methods=["GET"],
                summary=f"Get All {self.model.__name__} from the collection",
                description=f"Get All {self.model.__name__} from the collection",
            )
        if not self.disable_get_one:
            self._add_api_route(
                "/{id}",
                self._get_one(),
                response_model=self.model_out,
                dependencies=self.dependencies_get_one,
                methods=["GET"],
                summary=f"Get One {self.model.__name__} by {{id}} from the collection",
                description=f"Get One {self.model.__name__} by {{id}} from the collection",
            )
        if not self.disable_create_one:
            self._add_api_route(
                "/",
                self._create_one(),
                response_model=self.model_out,
                dependencies=self.dependencies_create_one,
                methods=["POST"],
                summary=f"Create One {self.model.__name__} in the collection",
                description=f"Create One {self.model.__name__} in the collection",
            )
        if not self.disable_update_one:
            self._add_api_route(
                "/{id}",
                self._update_one(),
                response_model=self.model_out,
                dependencies=self.dependencies_update_one,
                methods=["PATCH"],
                summary=f"Update One {self.model.__name__} by {{id}} in the collection",
                description=f"Update One {self.model.__name__} by {{id}} in the collection",
            )
        if not self.disable_replace_one:
            self._add_api_route(
                "/{id}",
                self._replace_one(),
                response_model=self.model_out,
                dependencies=self.dependencies_replace_one,
                methods=["PUT"],
                summary=f"Replace One {self.model.__name__} by {{id}} in the collection",
                description=f"Replace One {self.model.__name__} by {{id}} in the collection",
            )
        if not self.disable_delete_one:
            self._add_api_route(
                "/{id}",
                self._delete_one(),
                response_model=DeletedModelOut,
                dependencies=self.dependencies_delete_one,
                methods=["DELETE"],
                summary=f"Delete One {self.model.__name__} by {{id}} from the collection",
                description=f"Delete One {self.model.__name__} by {{id}} from the collection",
            )
