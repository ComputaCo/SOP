from abc import abstractmethod
from functools import cached_property
from typing import Any, Self

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
        return super().__init_subclass__()
