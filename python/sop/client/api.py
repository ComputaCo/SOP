from __future__ import annotations
import inspect
from typing import Any, Optional
from fastapi import FastAPI

import requests
from python.sop.base.api import BaseAPI
from python.sop.client.app import App

from python.sop.client.rpc import RPC
from python.sop.utils.parsing import JSONParser
from python.sop.utils.shortcircuit_merged import merged


class ClientAPI(BaseAPI):
    # just narrowing the types here
    prefix: str = None
    parent: ClientAPI = None
    # _merged_into_api, merge_aware_switch_dec = merged("_merged_into_api")
    _merged_into_api: Optional[ClientAPI] = None
    app: App = None

    # optionally, set these to be used as defaults for all requests
    headers_overrides: dict[str, str] = None
    params_overrides: dict[str, str] = None

    @property
    def default_headers(self) -> dict[str, str]:
        return {**self.parent.default_headers, **(self.headers_overrides or {})}

    @property
    def default_params(self) -> dict[str, str]:
        return {**self.parent.default_params, **(self.params_overrides or {})}

    # ... HTTP verb-specific decorators already defined in the base class

    def endpoint(self, verb, path=None):
        def decorator(fn):
            rettype = inspect.signature(fn).return_annotation
            parser = (
                JSONParser.for_type(rettype)
                if rettype != inspect.Signature.empty
                else None
            )

            def make_request(*args, **kwds):
                return self.rpc(
                    path or fn.__name__,
                    args,
                    kwds,
                    rpc_verb=verb,
                    rpc_ret_parser=parser,
                )

            return make_request

        return decorator

    def get_request(self, path, params=None, data=None, headers=None):
        return self.request("GET", path, params=None, data=None, headers=None)

    def post_request(self, path, params=None, data=None, headers=None):
        return self.request("POST", path, params=None, data=None, headers=None)

    def put_request(self, path, params=None, data=None, headers=None):
        return self.request("PUT", path, params=None, data=None, headers=None)

    def delete_request(self, path, params=None, data=None, headers=None):
        return self.request("DELETE", path, params=None, data=None, headers=None)

    def patch_request(self, path, params=None, data=None, headers=None):
        return self.request("PATCH", path, params=None, data=None, headers=None)

    def head_request(self, path, params=None, data=None, headers=None):
        return self.request("HEAD", path, params=None, data=None, headers=None)

    def options_request(self, path, params=None, data=None, headers=None):
        return self.request("OPTIONS", path, params=None, data=None, headers=None)

    def request(self, verb, path, params=None, data=None, headers=None):
        path = self._add_prefix(path)
        params.update(self.default_headers)
        headers.update(self.default_params)
        return requests.request(verb, path, params=params, data=data, headers=headers)

    def rpc(self, method_name, /, args, kwds, rpc_verb="POST", rpc_ret_parser=None):
        response = self.request(
            verb=rpc_verb,
            path="/rpc",
            data={"method": method_name, "args": args, "kwds": kwds},
            headers={"Content-Type": "application/json"},
        )
        return rpc_ret_parser.parse(response.json())

    def mount_sub_api(self, prefix: str, api: BaseAPI):
        api.parent = self
        return super().mount_sub_api(prefix, api)

    def merge(self, other: ClientAPI):
        """Merges another API into this one."""
        other.rpc = self.rpc
        other.request = self.request

    def __getattribute__(self, __name: str) -> Any:
        if __name == "_merged_into_api":
            return super().__getattribute__(__name)
        # if an API has been merged into another, then all lookups should be
        # performed on the merged-into API
        if self._merged_into_api is not None:
            return getattr(self._merged_into_api, __name)
        return super().__getattribute__(__name)
