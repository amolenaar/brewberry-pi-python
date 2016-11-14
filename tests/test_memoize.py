
from brewberry.memoize import memoize
import time

def test_should_call_decorated_function():
    called = []

    @memoize()
    def f(i):
        called.append(i)
        return i + 1

    assert f(0) == 1
    assert f(1) == 2
    assert f(2) == 3
    assert called == [0, 1, 2]

def test_should_remember_values():
    called = []

    @memoize()
    def f(i):
        called.append(i)
        return i + 1

    assert f(0) == 1
    assert f(0) == 1
    assert f(0) == 1
    assert called == [0], called


def test_should_allow_for_timeout():
    called = []

    @memoize(timeout=0.1)
    def f(i):
        called.append(i)
        return i + 1

    assert f(0) == 1
    time.sleep(0.2)
    assert f(0) == 1
    assert f(0) == 1
    assert called == [0, 0], called

def test_should_allow_for_timeout_with_noargs_functions():
    called = []

    @memoize(timeout=0.1)
    def f():
        called.append(0)

    f()
    time.sleep(0.2)
    f()
    f()
    assert called == [0, 0], called


# vim:sw=4:et:ai
