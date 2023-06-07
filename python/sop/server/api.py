from __future__ import annotations
import inspect
from typing import Any, Callable, Optional, Type

from fastapi import FastAPI
from fastapi.routing import APIRoute

from python.sop.base.api import BaseAPI
from python.sop.server.app import App
from python.sop.server.entity import ServerEntity
from python.sop.utils.parsing import JSONParser


class ServerAPI(BaseAPI):
    # just narrowing the types here
    prefix: str = None
    parent: ServerAPI = None
    app: App = None

    _fastapi: FastAPI = FastAPI()

    # ServerEntity sets this on __init_subclass__
    _rpc_entity_cls: Optional[Type[ServerEntity]]
    # ServerEntity sets this on __init__
    _rpc_entity_instance: Optional[ServerEntity]

    # ... HTTP verb-specific decorators already defined in the base class

    def endpoint(self, verb, path=None):
        """Returns decorator to register a function as an endpoint."""
        return self._fastapi.api_route(path, methods=[verb])

    cls_rpc_endpoint: Callable
    instance_rpc_endpoint: Callable
    jit_index_instance_rpc_endpoint: Callable

    def init_cls_rpc_endpoint(self):
        assert self._rpc_entity_cls is not None, "Must set _rpc_entity_cls first"

        @self.post_endpoint("/rpc")
        def cls_rpc_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            args, kwds = JSONParser.parse(args), JSONParser.parse(kwds)
            if hasattr(self._rpc_entity_cls, method_name):
                fn = getattr(self._rpc_entity_cls, method_name)
                if callable(fn) and inspect.ismethod(fn):
                    return fn(*args, **kwds)
            raise NotImplementedError

        self.cls_rpc_endpoint = cls_rpc_endpoint

    def init_instance_rpc_endpoint(self):
        assert (
            self._rpc_entity_instance is not None
        ), "Must set _rpc_entity_instance first"

        @self.post_endpoint("/rpc")
        def instance_rpc_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            args, kwds = JSONParser.parse(args), JSONParser.parse(kwds)
            if hasattr(self._rpc_entity_instance, method_name):
                fn = getattr(self._rpc_entity_instance, method_name)
                if callable(fn) and inspect.ismethod(fn):
                    return fn(*args, **kwds)
            raise NotImplementedError

        self.instance_rpc_endpoint = instance_rpc_endpoint

    def init_jit_index_instance_rpc_endpoint(self):
        assert self._rpc_entity_cls is not None, "Must set _rpc_entity_cls first"

        @self.post_endpoint("/rpc/{id}")
        def jit_index_instance_rpc_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            args, kwds = JSONParser.parse(args), JSONParser.parse(kwds)
            entity_instance = self._rpc_entity_cls.get_by_id(id)
            if hasattr(entity_instance, method_name):
                fn = getattr(entity_instance, method_name)
                if callable(fn) and inspect.ismethod(fn):
                    return fn(*args, **kwds)
            raise NotImplementedError

        self.jit_index_instance_rpc_endpoint = jit_index_instance_rpc_endpoint

    def mount_sub_api(self, child: ServerAPI):
        self._fastapi.mount(child.prefix, child._fastapi)
        return super().mount_sub_api(child)

    def merge(self, other: ServerAPI):
        """Merges another API into this one."""
        self._fastapi.router.routes.extend(other._fastapi.router.routes)
