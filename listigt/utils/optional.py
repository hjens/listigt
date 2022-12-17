from __future__ import annotations

from typing import TypeVar, Generic


class OptionalException(Exception):
    pass


T = TypeVar("T")


class Optional(Generic[T]):
    def __init__(self, value: T):
        self._value = value

    @classmethod
    def some(cls, value: T) -> Optional:
        return Optional(value)

    @classmethod
    def none(cls) -> Optional:
        return Optional(None)

    def value(self) -> T:
        if self._value:
            return self._value
        raise OptionalException()

    def value_or(self, default: T) -> T:
        return default if self._value is None else self._value
