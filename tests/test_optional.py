import pytest

from listigt.utils.optional import Optional, OptionalException


def test_value_for_some():
    optional_with_value: Optional[int] = Optional.some(3)
    assert optional_with_value.value() == 3

def test_value_raises_exception_for_none():
    optional_with_value: Optional[int] = Optional.none()
    with pytest.raises(OptionalException):
        optional_with_value.value()

def test_value_or():
    optional_with_value: Optional[int] = Optional.some(3)
    optional_without_value: Optional[int] = Optional.none()

    assert optional_with_value.value_or(5) == 3
    assert optional_without_value.value_or(5) == 5
