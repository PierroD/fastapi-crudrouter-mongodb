from typing import Any, Callable

from fastapi import HTTPException
from ...models.CRUDLookup import CRUDLookup
from .CRUDLookupRouterFactory import CRUDLookupRouterFactory
from . import CRUDLookupRouterRepository
from ...models.deleted_mongo_model import DeletedModelOut


class CRUDLookupRouter(CRUDLookupRouterFactory):
    def __init__(self, parent_router, child_args: CRUDLookup, *args, **kwargs):
        self.prefix = "/{id}/" + child_args.prefix
        self.db = parent_router.db
        self.model = child_args.model
        self.model_out = (
            child_args.model_out
            if child_args.model_out is not None
            else parent_router.model_out
        )
        self.collection_name = child_args.collection_name
        self.local_field = child_args.local_field
        self.foreign_field = child_args.foreign_field
        super().__init__(parent_router, child_args, *args, **kwargs)
        self._register_routes()

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str) -> self.parent_router.model:
            response = await CRUDLookupRouterRepository.get_all(
                self.db,
                self.collection_name,
                id,
                self.foreign_field,
                self.local_field,
                self.parent_router.collection_name,
                self.parent_router.model,
                self.model_out,
            )
            if response is None:
                raise HTTPException(404, "Empty collection")
            return response

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, lookup_id: str) -> self.parent_router.model:
            response = await CRUDLookupRouterRepository.get_one(
                self.db,
                self.collection_name,
                id,
                lookup_id,
                self.foreign_field,
                self.local_field,
                self.parent_router.collection_name,
                self.parent_router.model,
                self.model_out,
            )
            if response is None:
                raise HTTPException(404, "Document not found")
            return response

        return route

    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, data: self.model) -> self.parent_router.model:
            response = await CRUDLookupRouterRepository.create_one(
                self.db,
                self.collection_name,
                id,
                data,
                self.foreign_field,
                self.local_field,
                self.parent_router.collection_name,
                self.parent_router.model,
                self.model_out,
            )
            if response is None:
                raise HTTPException(422, "Document not created")
            return response

        return route

    def _replace_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: str, lookup_id: str, data: self.model
        ) -> self.parent_router.model:
            response = await CRUDLookupRouterRepository.replace_one(
                self.db,
                self.collection_name,
                id,
                lookup_id,
                data,
                self.foreign_field,
                self.local_field,
                self.parent_router.collection_name,
                self.parent_router.model,
                self.model_out,
            )
            if response is None:
                raise HTTPException(422, "Document not replaced")
            return response

        return route

    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: str, lookup_id: str, data: self.model
        ) -> self.parent_router.model:
            response = await CRUDLookupRouterRepository.update_one(
                self.db,
                self.collection_name,
                id,
                lookup_id,
                data,
                self.foreign_field,
                self.local_field,
                self.parent_router.collection_name,
                self.parent_router.model,
                self.model_out,
            )
            if response is None:
                raise HTTPException(422, "Document not updated")
            return response

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(id: str, lookup_id: str) -> DeletedModelOut:
            response = await CRUDLookupRouterRepository.delete_one(
                self.db, self.collection_name, lookup_id
            )
            if response is None:
                raise HTTPException(422, "Document not deleted")
            return response

        return route

    def _register_routes(self):
        self._add_api_route(
            path=self.prefix,
            endpoint=self._get_all(),
            response_model=self.model_out,
            methods=["GET"],
            summary=f"Get All {self.model.__name__} linked to a {self.parent_router.model.__name__}",
            description=f"Get All {self.model.__name__} linked to a {self.parent_router.model.__name__}",
        )
        self._add_api_route(
            path=self.prefix + "/{lookup_id}",
            endpoint=self._get_one(),
            response_model=self.model_out,
            methods=["GET"],
            summary=f"Get 0ne {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
            description=f"Get One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
        )
        self._add_api_route(
            path=self.prefix,
            endpoint=self._create_one(),
            response_model=self.model_out,
            methods=["POST"],
            summary=f"Create One {self.model.__name__} linked to a {self.parent_router.model.__name__}",
            description=f"Create One {self.model.__name__} linked to a {self.parent_router.model.__name__}",
        )
        self._add_api_route(
            path=self.prefix + "/{lookup_id}",
            endpoint=self._replace_one(),
            response_model=self.model_out,
            methods=["PUT"],
            summary=f"Replace One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
            description=f"Replace One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
        )
        self._add_api_route(
            path=self.prefix + "/{lookup_id}",
            endpoint=self._update_one(),
            response_model=self.model_out,
            methods=["PATCH"],
            summary=f"Update One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
            description=f"Update One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
        )
        self._add_api_route(
            path=self.prefix + "/{lookup_id}",
            endpoint=self._delete_one(),
            response_model=DeletedModelOut,
            methods=["DELETE"],
            summary=f"Delete One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
            description=f"Delete One {self.model.__name__} linked to a {self.parent_router.model.__name__} by lookup_id",
        )
