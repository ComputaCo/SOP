from __future__ import annotations

from abc import abstractmethod
from typing import Optional, Self

from python.sop.base.app import AbstractBaseApp


class BaseAPI:
    prefix: str = None
    parent: Optional[BaseAPI] = None
    app: AbstractBaseApp = None

    def get_endpoint(self, path=None):
        return self.endpoint("GET", path)

    def post_endpoint(self, path=None):
        return self.endpoint("POST", path)

    def put_endpoint(self, path=None):
        return self.endpoint("PUT", path)

    def delete_endpoint(self, path=None):
        return self.endpoint("DELETE", path)

    def patch_endpoint(self, path=None):
        return self.endpoint("PATCH", path)

    def head_endpoint(self, path=None):
        return self.endpoint("HEAD", path)

    def options_endpoint(self, path=None):
        return self.endpoint("OPTIONS", path)

    @abstractmethod
    def endpoint(self, verb, path):
        """Returns decorator to register a function as an endpoint."""
        pass

    def sub_api(self, prefix):
        sub_api = self.__class__()
        self.mount_sub_api(prefix, sub_api)
        return sub_api

    def mount_sub_api(self, prefix: str, api: BaseAPI):
        """Mounts a sub-api at the given prefix."""
        api.prefix = f"{self.prefix}/{prefix}" if self.prefix else prefix
        api.parent = self
        api.app = self.app
        return api

    @abstractmethod
    def merge(self, other: Self):
        """Merges another API into this one."""
        pass

    def _add_prefix(self, path):
        if path.startswith("/"):
            path = path[1:]
        return f"{self.prefix}/{path}" if self.prefix else path
