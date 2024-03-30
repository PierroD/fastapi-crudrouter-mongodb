from abc import abstractmethod
from typing import Any, Callable, Optional, Sequence
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends


class CRUDRouterFactory(APIRouter):
    """
    CRUDRouterFactory is an abstract class that implements the basic CRUD operations for a given model.

    :param model: The model to be used for the CRUD operations.
    :type model: MongoModel
    :param db: The database to be used for the CRUD operations.
    :type db: Database
    :param collection_name: The name of the collection to be used for the CRUD operations.
    :type collection_name: str
    :param args: The args to be passed to the APIRouter.
    :type args: Any
    :param kwargs: The kwargs to be passed to the APIRouter.
    :type kwargs: Any
    """

    def __init__(self, model, db, collection_name, *args, **kwargs):
        self.model = model
        self.collection_name = collection_name
        self.db = db
        super().__init__(*args, **kwargs)

    def _add_api_route(
        self,
        path: str,
        endpoint: Callable,
        dependencies: Optional[Sequence[Depends]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Add a new APIRoute to the router.

        :param path: The path for the APIRoute.
        :type path: str
        :param endpoint: The endpoint for the APIRoute.
        :type endpoint: Callable
        :param dependencies: The dependencies for the APIRoute.
        :type dependencies: Optional[Sequence[Depends]]
        :param kwargs: The kwargs to be passed to the APIRoute.
        :type kwargs: Any
        """
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
