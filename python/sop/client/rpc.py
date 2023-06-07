from dataclasses import dataclass
from typing import Any, Optional, Type
import attrs

import pydantic
from python.sop.client.api import ClientAPI

from python.sop.utils.parsing import JSON, JSONParser, ParsableType


@dataclass
class RPC:
    method_name: str
    controller: ClientAPI
    ret_parser: JSONParser = JSONParser()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.controller.rpc(self.method_name, args, kwds, self.ret_parser)
