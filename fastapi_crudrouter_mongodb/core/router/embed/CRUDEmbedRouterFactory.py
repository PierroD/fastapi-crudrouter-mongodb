from typing import Any, Callable
from fastapi import APIRouter

from ..CRUDRouterFactory import CRUDRouterFactory
from ...models.mongo_model import MongoModel


class CRUDEmbedRouterFactory(APIRouter):
    def __init__(
        self, parent_router: CRUDRouterFactory, child_args: MongoModel, *args, **kwargs
    ):
        self.parent_router = parent_router
        self.child_args = child_args

    def _add_api_route(self, path: str, endpoint: Callable, **kwargs: Any) -> None:
        self.parent_router._add_api_route(path, endpoint, **kwargs)

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return self.parent_router._get_all(*args, **kwargs)

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return self.parent_router._get_one(*args, **kwargs)

    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return self.parent_router._create_one(*args, **kwargs)

    def _replace_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return self.parent_router._update_one(*args, **kwargs)

    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return self.parent_router._delete_one(*args, **kwargs)

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        return self.parent_router._delete_one(*args, **kwargs)
