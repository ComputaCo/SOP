from abc import abstractmethod
from functools import cached_property
from typing import Any, Self

import pydantic
from python.sop.client.api import ClientAPI, SubController

from python.sop.base.entity import BaseEntity
from python.sop.client.app import App
from python.sop.client.rpc import RPC
from python.sop.utils.parsing import ClassParser, JSONParser


class ClientEntity(BaseEntity):
    """Not intended for direct subclassing. Use `app.Entity` instead."""

    class Meta(BaseEntity.Meta):
        # restated for type narrowing
        # don't assign either though, they will be set by the app.Entity method
        # use cls.controller to access the class level controller
        # use self.controller to access the instance level controller
        api: ClientAPI
        app: App

    def __init__(self) -> None:
        # suppose the class level controller is at /<type>,
        # then the instance level controller is at /<type>/<id>
        self.api = self.__class__.api.sub_api(self.id)
        super().__init__()

    @classmethod
    def create(cls, **kwargs):
        # POST `<host>/<type>/create` {**kwargs}
        return cls.api.post_request("/create", **kwargs)

    @classmethod
    def get_by_id(cls, id: str) -> Self:
        # GET `<host>/<type>/<id>`
        return cls.api.get_request(f"/{id}")

    @classmethod
    def get_many(cls, ids: list[str]) -> list[Self]:
        # GET `<host>/<type>&ids=<ids>`
        return cls.api.get_request("", params={"ids": ids})

    @classmethod
    def get_all(cls) -> list[Self]:
        # GET `<host>/<type>`
        return cls.api.get_request("")

    @classmethod
    def update_by_id(cls, id: int, data: Self):
        # POST `<host>/<type>/<id>/update` {**data}
        return cls.api.put_request(f"/{id}", data=data.dict())

    def push_updates(self):
        self.update_by_id(self.id, self)

    def pull_updates(self):
        # POST `<host>/<type>/<id>/pull_updates`
        updated_self = self.get_by_id(self.id)
        self.__dict__.update(updated_self.__dict__)

    @classmethod
    def delete_by_id(cls, id: int):
        # DELETE `<host>/<type>/<id>`
        cls.api.delete_request(f"/{id}")

    def delete(self):
        self.delete_by_id(self.id)

    @cached_property
    @classmethod
    def parser(cls) -> ClassParser[Self]:
        return ClassParser(T=cls)

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError as e:
            if self.app.auto_rpc:
                return RPC(self.api, __name)
            raise e

    def __init_subclass__(cls) -> None:
        # create parser so the JSONParser has it in its registry
        _ = cls.parser()
        return super().__init_subclass__()
