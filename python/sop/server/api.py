from __future__ import annotations
import functools
import inspect
from typing import Any, Callable, Optional, Type

from fastapi import FastAPI, HTTPException
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

    cls_rpc_get_endpoint: Callable
    cls_rpc_post_endpoint: Callable
    instance_rpc_get_endpoint: Callable
    instance_rpc_post_endpoint: Callable
    jit_index_instance_rpc_get_endpoint: Callable
    jit_index_instance_rpc_post_endpoint: Callable

    def init_cls_rpc_endpoint(self):
        assert self._rpc_entity_cls is not None, "Must set _rpc_entity_cls first"

        def _cls_rpc_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            args, kwds = JSONParser.parse(args), JSONParser.parse(kwds)
            if hasattr(self._rpc_entity_cls, method_name):
                fn = getattr(self._rpc_entity_cls, method_name)
                if callable(fn) and inspect.ismethod(fn):
                    return fn(*args, **kwds)
            raise NotImplementedError

        @self.get_endpoint("/rpc")
        def cls_rpc_get_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            return _cls_rpc_endpoint(method_name, args, kwds)

        self.cls_rpc_get_endpoint = cls_rpc_get_endpoint

        @self.post_endpoint("/rpc")
        def cls_rpc_post_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            return _cls_rpc_endpoint(method_name, args, kwds)

        self.cls_rpc_post_endpoint = cls_rpc_post_endpoint

    def init_instance_rpc_endpoint(self):
        assert (
            self._rpc_entity_instance is not None
        ), "Must set _rpc_entity_instance first"

        def _instance_rpc_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            args, kwds = JSONParser.parse(args), JSONParser.parse(kwds)
            if hasattr(self._rpc_entity_instance, method_name):
                fn = getattr(self._rpc_entity_instance, method_name)
                if callable(fn) and inspect.ismethod(fn):
                    return fn(*args, **kwds)
            raise NotImplementedError

        @self.get_endpoint("/rpc")
        def instance_rpc_get_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            return _instance_rpc_endpoint(method_name, args, kwds)

        self.instance_rpc_get_endpoint = instance_rpc_get_endpoint

        @self.post_endpoint("/rpc")
        def instance_rpc_post_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            return _instance_rpc_endpoint(method_name, args, kwds)

        self.instance_rpc_post_endpoint = instance_rpc_post_endpoint

    def init_jit_index_instance_rpc_endpoint(self):
        assert self._rpc_entity_cls is not None, "Must set _rpc_entity_cls first"

        @self.post_endpoint("/rpc/{id}")
        def _jit_index_instance_rpc_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            args, kwds = JSONParser.parse(args), JSONParser.parse(kwds)
            entity_instance = self._rpc_entity_cls.get_by_id(id)
            if hasattr(entity_instance, method_name):
                fn = getattr(entity_instance, method_name)
                if callable(fn) and inspect.ismethod(fn):
                    return fn(*args, **kwds)
            raise NotImplementedError

        @self.post_endpoint("/rpc/{id}")
        def jit_index_instance_rpc_get_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            return _jit_index_instance_rpc_endpoint(method_name, args, kwds)

        self.jit_index_instance_rpc_get_endpoint = jit_index_instance_rpc_get_endpoint

        @self.post_endpoint("/rpc/{id}")
        def jit_index_instance_rpc_post_endpoint(
            method_name: str, args: list[Any], kwds: dict[str, Any]
        ) -> Any:
            return _jit_index_instance_rpc_endpoint(method_name, args, kwds)

        self.jit_index_instance_rpc_post_endpoint = jit_index_instance_rpc_post_endpoint

    def mount_sub_api(self, child: ServerAPI):
        self._fastapi.mount(child.prefix, child._fastapi)
        return super().mount_sub_api(child)

    def access_control(self, *attrs, predicate):
        # must be associated with an entity for this to work
        for attr in attrs:
            if isinstance(attr, str):
                self._rpc_entity_cls.Meta._access_restrictions[attr] = predicate
            elif hasattr(attr, "__name__"):
                self._rpc_entity_cls.Meta._access_restrictions[attr.__name__] = predicate
            else:
                raise ValueError(
                    f"Invalid hidden attribute {attr}. Must be str or have __name__ defined."
                )
        if len(attrs) == 1:
            return attrs[0]

    def hidden(self, *attrs):
        return self.access_control(*attrs, predicate=lambda entity: False)

    def merge(self, other: ServerAPI):
        """Merges another API into this one."""
        self._fastapi.router.routes.extend(other._fastapi.router.routes)
