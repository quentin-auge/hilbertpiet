from copy import deepcopy

from piet.context import Context


def test_same_context():
    c1 = Context(stack=[1, 2, 3], buffer=4)
    c2 = Context(stack=[1, 2, 3], buffer=4)
    assert c1 == c2


def test_distinct_stack():
    c1 = Context(stack=[1, 2, 3], buffer=4)
    c2 = Context(stack=[1, 3], buffer=4)
    assert c1 != c2


def test_distinct_buffer():
    c1 = Context(stack=[1, 2, 3], buffer=4)
    c2 = Context(stack=[1, 2, 3], buffer=5)
    assert c1 != c2


def test_repr():
    c = Context(stack=[1, 2, 3], buffer=4)
    assert repr(c) == 'Context(stack = [1, 2, 3], buffer = 4)'


def test_repr_no_stack():
    c = Context(buffer=4)
    assert repr(c) == 'Context(stack = [], buffer = 4)'


def test_repr_no_buffer():
    c = Context(stack=[1, 2, 3])
    assert repr(c) == 'Context(stack = [1, 2, 3])'


def test_str():
    c = Context(stack=[1, 2, 3], buffer=4)
    assert str(c) == '[1, 2, 3]  4'


def test_str_no_stack():
    c = Context(buffer=4)
    assert str(c) == '[]  4'


def test_str_no_buffer():
    c = Context(stack=[1, 2, 3])
    assert str(c) == '[1, 2, 3]'


def test_deepcopy():
    c1 = Context(stack=[1, 2, 3], buffer=4)
    c2 = deepcopy(c1)

    assert c1 == c2
    assert c1.stack is not c2.stack
