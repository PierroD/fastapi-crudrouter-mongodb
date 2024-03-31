from typing import Any, Callable, Sequence
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.params import Depends
from .CRUDRouterFactory import CRUDRouterFactory
from . import CRUDRouterRepository
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
        """
        Get all documents from the collection.

        :return: A list of documents from the collection.
        :rtype: list
        """

        async def route() -> list:
            response = await CRUDRouterRepository.get_all(
                self.db, self.model, self.collection_name, self.model_out
            )
            return response if len(response) else []

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Get one document from the collection.

        :param id: The id of the document to be retrieved.
        :type id: str
        :return: The document from the collection.
        :rtype: dict
        """

        async def route(id: str) -> self.model:
            response = await CRUDRouterRepository.get_one(
                self.db, self.model, self.collection_name, id, self.model_out
            )
            if response is None:
                raise HTTPException(404, "Document not found")
            return response

        return route

    """
    Create one document in the collection.

    :param data: The data of the document to be created.
    :type data: dict
    :return: The created document.
    :rtype: dict
    """

    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(data: self.model) -> self.model:
            response = await CRUDRouterRepository.create_one(
                self.db, self.model, self.collection_name, data, self.model_out
            )
            if response is None:
                raise HTTPException(422, "Document not created")
            return response

        return route

    def _replace_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Replace one document in the collection.

        :param id: The id of the document to be replaced.
        :type id: str
        :param data: The data of the document to be replaced.
        :type data: dict
        :return: The replaced document.
        :rtype: dict
        """

        async def route(id: str, data: self.model) -> self.model:
            response = await CRUDRouterRepository.replace_one(
                self.db, self.model, self.collection_name, id, data, self.model_out
            )
            if response is None:
                raise HTTPException(422, "Document not replaced")
            return response

        return route

    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Update one document in the collection.

        :param id: The id of the document to be updated.
        :type id: str
        :param data: The data of the document to be updated.
        :type data: dict
        :return: The updated document.
        :rtype: dict
        """

        async def route(id: str, data: self.model) -> self.model:
            response = await CRUDRouterRepository.update_one(
                self.db, self.model, self.collection_name, id, data, self.model_out
            )
            if response is None:
                raise HTTPException(422, "Document not updated")
            return response

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """
        Delete one document from the collection.

        :param id: The id of the document to be deleted.
        :type id: str
        :return: The deleted document id.
        :rtype: dict {"id": "{deleted_id}"}
        """

        async def route(id: str) -> DeletedModelOut:
            response = await CRUDRouterRepository.delete_one(
                self.db, self.collection_name, id
            )
            if response is None:
                raise HTTPException(422, "Document not deleted")
            return response

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
