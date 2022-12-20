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

def test_value_or_none():
    assert Optional.none().value_or_none() is None
    assert Optional.some(1).value_or_none() == 1


def test_get_attribute():
    class Foo:
        member = 1

        def func_returns_value(self, arg):
            return 1 + arg

        def func_returns_none(self):
            return None

        def func_returns_optional(self):
            return Optional.some(10)

    optional_foo = Optional.some(Foo())
    assert optional_foo.func_returns_value(2).value() == 3
    assert optional_foo.member.value() == 1
    assert not optional_foo.func_returns_none().has_value()
    assert optional_foo.func_returns_optional().value() == 10


def test_method_chaining():
    class Foo:
        def echo(self, arg):
            return arg

        def echo_multiple_args(self, arg1, arg2):
            return arg1, arg2

        def echo_nothing(self):
            return None

    optional_foo1 = Optional.some(Foo())
    optional_foo2 = Optional.some(Foo())
    assert optional_foo1.echo(optional_foo2).echo(3).value() == 3
    assert not optional_foo1.echo(None).echo(3).has_value()
    assert not optional_foo1.echo(None).echo_multiple_args(3, 5).has_value()
    assert not optional_foo1.echo(None).echo_nothing().has_value()
