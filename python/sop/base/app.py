from abc import abstractmethod
from typing import Type

import stringcase

from python.sop.base.api import BaseAPI
from python.sop.base.entity import BaseEntity
from python.sop.utils.strings import camelize


class AbstractBaseApp(BaseAPI):
    endpoint: str
    auto_rpc: bool = True

    T_Entity: Type[BaseEntity]

    def __post_init__(self) -> None:
        self.app = self

    def Entity(self) -> Type[BaseEntity]:
        class Entity(self.T_Entity):
            class Meta(self.T_Entity.Meta):
                app = self

        return Entity

    @abstractmethod
    def init_schema(self):
        pass

    # @abstractmethod
    # def init_api(self):
    #     pass


def MakeBaseApp(T_API: Type[BaseAPI], T_Entity: Type[BaseEntity]):
    _T_Entity = T_Entity

    class App(AbstractBaseApp, T_API):
        T_Entity = _T_Entity

    return App
