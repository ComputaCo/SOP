from abc import abstractmethod
from typing import Generic, Self, TypeVar

from python.sop.base.api import BaseAPI
from python.sop.base.app import AbstractBaseApp
from python.sop.utils.strings import camelize


T_BaseAPI = TypeVar("T_BaseAPI", bound=BaseAPI)
T_App = TypeVar("T_App", bound=AbstractBaseApp)


class BaseEntity(Generic[T_BaseAPI, T_App]):
    id: str  # all entities have an id # TODO: make this a UUID

    class Meta:
        api: T_BaseAPI  # subclasses should override, merged across all bases in __init_subclass__
        app: T_App  # set in the base entity. inherited by all subclasses

    @property
    def guid(self) -> str:
        return f"{self.__class__.__name__}:{self.id}"

    @abstractmethod
    @classmethod
    def create(cls, **kwargs):
        pass

    @abstractmethod
    @classmethod
    def get_by_id(cls, id: int) -> Self:
        pass

    @abstractmethod
    @classmethod
    def get_many(cls, ids: list[int]) -> list[Self]:
        pass

    @abstractmethod
    @classmethod
    def get_all(cls) -> list[Self]:
        pass

    @abstractmethod
    @classmethod
    def update_by_id(cls, id: int, data: Self):
        pass

    def sync(self):
        self.push_updates()
        self.pull_updates()

    @abstractmethod
    def push_updates(self):
        pass

    @abstractmethod
    def pull_updates(self):
        pass

    @abstractmethod
    @classmethod
    def delete_by_id(cls, id: int):
        pass

    @abstractmethod
    def delete(self):
        pass

    def __new__(cls) -> Self:
        id = cls.create()
        return cls.get_by_id(id)

    def __del__(self):
        self.delete()

    def __init_subclass__(cls) -> None:
        # merge all cls api's into the app api at the cls level
        ## get or create the cls's personal api
        ### To do this, we're going to check if the cls's api equals any of its parents' apis
        ### If it does, we'll make a special one just for the cls
        if any([cls.api == base.api for base in cls.__bases__]):
            cls._get_meta().api = T_BaseAPI()
        ## Next, merge all of the cls's parents' apis into the cls's api
        for base in cls.__bases__:
            cls.api.merge(base.api)

        # Finally, mount it under the app level api
        cls._get_meta().app.mount_sub_api(
            prefix=camelize(cls.__name__), api=cls._get_meta().api
        )

    def __init__(self) -> None:
        super().__init__()

        # create an instance-level API
        class Meta(self._get_meta()):
            api = self._get_meta().api.sub_api(self.id)

        self.Meta = Meta

    @classmethod
    def _get_meta(cls):
        if vars(cls).get("Meta", None) is None:
            cls.Meta = type("Meta", (BaseEntity.Meta,), {})
        if not issubclass(cls.Meta, BaseEntity.Meta):
            # this allows them to share the same app attribute
            BaseEntity.Meta.__init_subclass__(cls.Meta)
        return cls.Meta
