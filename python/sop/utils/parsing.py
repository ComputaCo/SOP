from __future__ import annotations

from abc import abstractmethod
import dataclasses
from typing import Any, Generic, Type, TypeVar
from pydantic import BaseModel

S = TypeVar("S")
T = TypeVar("T")


class AbstractParser(Generic[S, T]):
    S: Type[S]
    T: Type[T]

    @abstractmethod
    def parse(self, data: S) -> T:
        pass


JSON = None | int | float | bool | str | list["JSON"] | dict[str, "JSON"]
ParsableType = (
    None
    | int
    | float
    | bool
    | str
    | list["ParsableType"]
    | dict[str, "ParsableType"]
    | BaseModel
    | Any
)


class JSONParser(Generic[T], AbstractParser[JSON, T]):
    S = JSON

    __parsers = []
    __parsers_by_type = {}

    def __init__(self, T: Type[T]) -> None:
        if T is not self.T:
            raise ValueError(f"Cannot build parser for {T} with {self.__class__}")
        self.__parsers.append(self)
        self.__parsers_by_type[self.T] = self
        super().__init__()

    def parse(self, data: JSON) -> T:
        # TODO: modify this to first attempt the most specific parser, then the least specific (lower priority)
        for parser in self.__parsers:
            try:
                return parser.parse(data)
            except:
                continue
        raise Exception(f"Could not parse {data} to {self.__class__.__name__}")

    @classmethod
    def for_type(cls, T: Type[T]) -> JSONParser[T]:
        if T in cls.__parsers_by_type:
            return cls.__parsers_by_type[T]
        else:
            for ParserImplementation in cls.__subclasses__():
                if ParserImplementation.T == T:
                    return ParserImplementation(T)


json_parser = JSONParser()


class NoneParser(JSONParser[None]):
    T = None

    def parse(self, data: JSON) -> None:
        if data is not None:
            raise Exception(f"Could not parse {data} to None")
        return None


none_parser = NoneParser()


class IntParser(JSONParser[int]):
    T = int

    def parse(self, data: JSON) -> int:
        return int(data)


int_parser = IntParser()


class FloatParser(JSONParser[float]):
    T = float

    def parse(self, data: JSON) -> float:
        return float(data)


float_parser = FloatParser()


class BoolParser(JSONParser[bool]):
    T = bool

    def parse(self, data: JSON) -> bool:
        return bool(data)


bool_parser = BoolParser()


class StrParser(JSONParser[str]):
    T = str

    def parse(self, data: JSON) -> str:
        return str(data)


str_parser = StrParser()


class ListParser(JSONParser[list]):
    T = list[JSON]

    def parse(self, data: JSON) -> list:
        if not isinstance(data, list):
            raise Exception(f"Could not parse {data} to list")
        return [JSONParser.parse(item) for item in data]


list_parser = ListParser()


class MapParser(JSONParser[dict[str, JSON]]):
    T = dict[str, JSON]

    def parse(self, data: JSON) -> dict:
        if not isinstance(data, dict):
            raise Exception(f"Could not parse {data} to dict")
        return {str(key): JSONParser.parse(value) for key, value in data.items()}


map_parser = MapParser()


class ClassParser(Generic[T], JSONParser[T]):
    T: Type[Any] = attr.ib()

    def parse(self, data: JSON) -> BaseModel:
        kwargs = map_parser.parse(data)
        return self.T(**kwargs)
