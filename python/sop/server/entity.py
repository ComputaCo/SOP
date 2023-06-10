from abc import abstractmethod
from functools import cached_property
import inspect
from typing import Any, Callable, Self
from fastapi import HTTPException

import pydantic
from python.sop.client.api import ClientAPI, SubController

from python.sop.base.entity import BaseEntity
from python.sop.server.app import App
from python.sop.server.api import ServerAPI
from python.sop.utils.parsing import ClassParser, JSONParser


class ServerEntity(BaseEntity):
    """Not intended for direct subclassing. Use `app.Entity` instead."""

    class Meta(BaseEntity.Meta):
        # restated for type narrowing
        # don't assign either though, they will be set by the app.Entity method
        # use cls.controller to access the class level controller
        # use self.controller to access the instance level controller
        api: ServerAPI = ServerAPI()
        app: App

        _access_restrictions: dict[str, Callable] = {}
        _access_restrictions: dict[str, Callable] = {}

        def __init_subclass__(cls) -> None:
            super().__init_subclass__()
            cls._access_restrictions = cls._access_restrictions.copy()

    @Meta.api.post_endpoint("/create")
    @classmethod
    def create(cls, **kwargs):
        ...

    @Meta.api.get_endpoint("/{id}")
    @classmethod
    def get_by_id(cls, id: str) -> Self:
        ...

    @Meta.api.get_endpoint("/many")
    @classmethod
    def get_many(cls, ids: list[str]) -> list[Self]:
        ...

    @Meta.api.get_endpoint("/")
    @classmethod
    def get_all(cls) -> list[Self]:
        ...

    @Meta.api.put_endpoint("/{id}")
    @classmethod
    def update_by_id(cls, id: int, data: Self):
        ...

    @Meta.api.delete_endpoint("/{id}")
    @classmethod
    def delete_by_id(cls, id: int):
        ...

    def __init_subclass__(cls) -> None:
        cls.app.db.Entity.__init_subclass__(cls)
        cls.Meta.api._rpc_entity_cls = cls
        return super().__init_subclass__()

    def __init__(self) -> None:
        super().__init__()
        self.Meta = type("Meta", (self.Meta,), {})
        self.Meta.api._rpc_entity_instance = self

    def __getattribute__(self, __name: str) -> Any:
        if __name in ( 'Meta', '_access_restrictions'):
            return super().__getattribute__(__name)
        if __name in self.Meta._access_restrictions:
            if not self.Meta._access_restrictions[__name](self):
                raise HTTPException(status_code=403, detail="Forbidden")
        return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in self.Meta._access_restrictions:
            if not self.Meta._access_restrictions[__name](self):
                raise HTTPException(status_code=403, detail="Forbidden")
        return super().__setattr__(__name, __value)
