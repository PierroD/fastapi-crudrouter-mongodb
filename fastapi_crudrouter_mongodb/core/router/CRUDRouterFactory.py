

from abc import abstractmethod
from typing import Any, Callable, Optional, Sequence
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends


class CRUDRouterFactory(APIRouter):

    def __init__(self, model, db, collection_name, *args, **kwargs):
        self.model = model
        self.collection_name = collection_name
        self.db = db
        super().__init__(*args, **kwargs)

    def _add_api_route(
            self,
            path: str,
            endpoint: Callable,
            dependencies:Optional[Sequence[Depends]] = None,
            **kwargs: Any) -> None:
        super().add_api_route(path, endpoint, dependencies=dependencies, **kwargs)

    @abstractmethod
    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _create_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _replace_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _update_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _raise(self, e: Exception, status_code: int = 422) -> HTTPException:
        raise HTTPException(422, ", ".join(e.args)) from e
