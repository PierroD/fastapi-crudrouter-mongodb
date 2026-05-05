import json
from typing import Annotated, Any, Callable
from fastapi import HTTPException, Query, Path, status

from ...models.CRUDEmbed import CRUDEmbed
from ...models.deleted_mongo_model import DeletedModelOut
from ...utils.sorting import normalize_order_by

from .CRUDEmbedRouterFactory import CRUDEmbedRouterFactory
from ...factories import CRUDEmbedRouterRepository


def _to_lower_camel_case(snake_str: str) -> str:
    if snake_str.startswith("_"):
        return snake_str
    components = snake_str.lower().split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


class CRUDEmbedRouter(CRUDEmbedRouterFactory):
    def __init__(self, parent_router, child_args: CRUDEmbed, *args, **kwargs) -> None:
        self.identifier_display = (
            parent_router.identifier_field
            if parent_router.identifier_field != "_id"
            else "id"
        )
        self.parent_identifier_field = parent_router.identifier_field
        # MongoDB field name (camelCase, matching how to_mongo stores it)
        self.embed_identifier_field = _to_lower_camel_case(child_args.identifier_field)
        # URL display name (original value as provided by the user)
        self.embed_identifier_display = (
            child_args.identifier_field
            if child_args.identifier_field != "_id"
            else "embed_id"
        )
        self.prefix = f"/{{{self.identifier_display}}}/{child_args.embed_name}"
        self.db = parent_router.db
        self.model = child_args.model
        self.embed_name = child_args.embed_name
        super().__init__(parent_router, child_args, *args, **kwargs)
        self._register_routes()

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: Annotated[str, Path(alias=self.identifier_display)],
            skip: int | None = Query(None, ge=0),
            limit: int | None = Query(None, ge=1),
            sort_by: str | None = Query(None),
            order_by: str | None = Query(None),
            filters: str | None = Query(None),
        ) -> list[Any]:
            filters_dict = None
            if filters is not None:
                try:
                    filters_dict = json.loads(filters)
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "Invalid JSON in filters parameter",
                    ) from e
            try:
                normalized_order_by = normalize_order_by(order_by)
            except ValueError as e:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    str(e),
                ) from e
            response = await CRUDEmbedRouterRepository.get_all(
                self.db,
                id,
                self.parent_router.collection_name,
                self.embed_name,
                self.model,
                skip,
                limit,
                sort_by,
                normalized_order_by,
                filters_dict,
                self.parent_identifier_field,
            )
            return response if len(response) else []

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: Annotated[str, Path(alias=self.identifier_display)],
            embed_id: Annotated[str, Path(alias=self.embed_identifier_display)],
        ) -> self.model:
            response = await CRUDEmbedRouterRepository.get_one(
                self.db,
                id,
                embed_id,
                self.parent_router.collection_name,
                self.embed_name,
                self.model,
                self.parent_identifier_field,
                self.embed_identifier_field,
            )
            if response is None:
                raise HTTPException(404, "Document not found")
            return response

        return route

    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: Annotated[str, Path(alias=self.identifier_display)],
            data: self.model,
        ) -> self.model:
            response = await CRUDEmbedRouterRepository.create_one(
                self.db,
                id,
                self.parent_router.collection_name,
                self.embed_name,
                data,
                self.model,
                self.parent_identifier_field,
            )
            if response is None:
                raise HTTPException(422, "Document not created")
            return response

        return route

    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: Annotated[str, Path(alias=self.identifier_display)],
            embed_id: Annotated[str, Path(alias=self.embed_identifier_display)],
            data: self.model,
        ) -> self.model:
            response = await CRUDEmbedRouterRepository.update_one(
                self.db,
                id,
                embed_id,
                self.parent_router.collection_name,
                self.embed_name,
                data,
                self.model,
                self.parent_identifier_field,
                self.embed_identifier_field,
            )
            if response is None:
                raise HTTPException(422, "Document not updated")
            return response

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        async def route(
            id: Annotated[str, Path(alias=self.identifier_display)],
            embed_id: Annotated[str, Path(alias=self.embed_identifier_display)],
        ) -> DeletedModelOut:
            response = await CRUDEmbedRouterRepository.delete_one(
                self.db,
                id,
                embed_id,
                self.parent_router.collection_name,
                self.embed_name,
                self.model,
                self.parent_identifier_field,
                self.embed_identifier_field,
            )
            if response is None:
                raise HTTPException(422, "Document not deleted")
            return response

        return route

    def _register_routes(self) -> None:
        self._add_api_route(
            path=self.prefix,
            endpoint=self._get_all(),
            methods=["GET"],
            response_model=list[self.model],
            tags=[self.embed_name],
            summary=f"Get All {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
            description=f"Get All {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
        )
        embed_id_segment = f"/{{{self.embed_identifier_display}}}"
        self._add_api_route(
            path=self.prefix + embed_id_segment,
            endpoint=self._get_one(),
            methods=["GET"],
            response_model=self.model,
            tags=[self.embed_name],
            summary=f"Get One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
            description=f"Get One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
        )
        self._add_api_route(
            path=self.prefix,
            endpoint=self._create_one(),
            methods=["POST"],
            response_model=self.model,
            tags=[self.embed_name],
            summary=f"Create One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
            description=f"Create One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
        )
        self._add_api_route(
            path=self.prefix + embed_id_segment,
            endpoint=self._update_one(),
            methods=["PATCH"],
            response_model=self.model,
            tags=[self.embed_name],
            summary=f"Update One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
            description=f"Update One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
        )
        self._add_api_route(
            path=self.prefix + embed_id_segment,
            endpoint=self._delete_one(),
            methods=["DELETE"],
            response_model=DeletedModelOut,
            tags=[self.embed_name],
            summary=f"Delete One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
            description=f"Delete One {self.model.__name__} embedded into a {self.parent_router.model.__name__}",
        )
