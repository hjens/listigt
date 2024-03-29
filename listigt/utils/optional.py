from __future__ import annotations

from copy import copy, deepcopy
from typing import TypeVar, Generic, Iterable


class OptionalException(Exception):
    pass


class CallableWrapper:
    def __init__(self, callable):
        self._callable = callable

    def __call__(self, *args, **kwargs):
        value = self._callable(*args, **kwargs)
        if value is None:
            return Optional.none()
        elif isinstance(value, Optional):
            return value
        return Optional.some(value)


T = TypeVar("T")


class Optional(Generic[T]):
    def __init__(self, value: T | None):
        self._value = value
        self.__cached_attrs = {}

    @classmethod
    def some(cls, value: T) -> Optional:
        return Optional(value)

    @classmethod
    def none(cls) -> Optional:
        return Optional(None)

    def has_value(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return not self.has_value()

    def value(self) -> T:
        if self.has_value():
            return self._value
        raise OptionalException()

    def value_or(self, default: T) -> T:
        return self._value if self.has_value() else default

    def value_or_none(self) -> T | None:
        return self._value if self.has_value() else None

    def __copy__(self):
        if self.is_none():
            return Optional.none()
        return Optional.some(copy(self.value()))

    def __deepcopy__(self, memodict={}):
        if self.is_none():
            return Optional.none()
        return Optional.some(deepcopy(self.value(), memodict))

    def __dir__(self) -> Iterable[str]:
        return set(super().__dir__()).union(set(self.value().__dir__()))

    def __str__(self):
        if self.is_none():
            return "Optional(None)"
        return f"Optional[{self.value()}]"

    def __repr__(self):
        return str(self)

    def __getattribute__(self, item):
        try:
            # Is it an attribute defined on the Optional class? E.g. value()
            return super().__getattribute__(item)
        except AttributeError:
            # If self has no value, make a function that always returns none()
            if self.is_none():
                def return_none(*args, **kwargs):
                    return Optional.none()
                return CallableWrapper(return_none)
            # Get the attribute from the value
            attribute = self.value().__getattribute__(item)
            # If the attribute is a callable, wrap it before returning,
            # so it will return an Optional
            if hasattr(attribute, "__call__"):
                return CallableWrapper(attribute)
            # Attribute is a member, put it inside an optional
            return Optional.some(attribute)
