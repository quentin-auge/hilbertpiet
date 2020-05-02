from copy import deepcopy

from piet.context import Context


def test_str():
    c = Context(stack=[1, 2, 3], value=4)
    assert str(c) == '[1, 2, 3] 4'
