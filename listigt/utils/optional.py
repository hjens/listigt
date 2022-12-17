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

    def has_value(self) -> bool:
        return self._value is not None

    def value(self) -> T:
        if self.has_value():
            return self._value
        raise OptionalException()

    def value_or(self, default: T) -> T:
        return self._value if self.has_value() else default
