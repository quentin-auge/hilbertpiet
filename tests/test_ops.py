from copy import deepcopy

import pytest

from piet.context import Context
from piet.ops import Add, Duplicate, Init, Op, Push, Resize


def test_ops_purity():
    class TestOp(Op):
        def _call(self, context: Context) -> Context:
            context.stack = [18]
            context.value = 32
            return context

    op = TestOp()

    context = Context(stack=[1, 2, 3], value=4)
    context1 = deepcopy(context)
    context2 = deepcopy(context)

    expected_context = Context(stack=[18], value=32)

    # `Op._call()` mutates the context
    mutated_context = op._call(context1)
    assert mutated_context is context1
    assert mutated_context == expected_context
    assert context1 == expected_context

    # `Op.__call__()` creates a new context
    new_context = op(context2)
    assert new_context is not context2
    assert new_context == expected_context
    assert context2 == context


def test_init():
    op = Init()
    context = Context()
    expected_context = Context(value=1)
    assert op(context) == expected_context


def test_init_nonempty_context():
    op = Init()
    context = Context(stack=[1, 2, 3], value=4)
    with pytest.raises(RuntimeError, match='Invalid non-empty context'):
        print(op(context))


def test_resize():
    op = Resize(5)
    context = Context(stack=[1, 2, 3], value=4)
    expected_context = Context(stack=[1, 2, 3], value=5)
    assert op(context) == expected_context


def test_resize_null_value():
    op = Resize(0)
    context = Context()
    with pytest.raises(RuntimeError, match='Invalid non-positive resize value'):
        print(op(context))


def test_resize_negative_value():
    op = Resize(-4)
    context = Context()
    with pytest.raises(RuntimeError, match='Invalid non-positive resize value'):
        print(op(context))


def test_push():
    op = Push()
    context = Context(stack=[1, 2, 3], value=4)
    expected_context = Context(stack=[1, 2, 3, 4], value=1)
    assert op(context) == expected_context


def test_push_null_value():
    op = Push()
    context = Context()
    with pytest.raises(RuntimeError, match='Invalid non-positive push value'):
        print(op(context))


def test_push_negative_value():
    op = Push()
    context = Context(value=-4)
    with pytest.raises(RuntimeError, match='Invalid non-positive push value'):
        print(op(context))


def test_duplicate():
    op = Duplicate()
    context = Context(stack=[1, 2, 3])
    expected_context = Context(stack=[1, 2, 3, 3])
    assert op(context) == expected_context


def test_add():
    op = Add()
    context = Context(stack=[1, 2, 3])
    expected_context = Context(stack=[1, 5])
    assert op(context) == expected_context
