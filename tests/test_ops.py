from piet.context import Context
from piet.ops import Add


def test_add():
    op = Add()

    context = Context(stack=[1, 2, 3])
    expected_context = Context(stack=[1, 5])

    assert op(context) == expected_context
