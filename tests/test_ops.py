from copy import deepcopy
from dataclasses import dataclass

import pytest

from piet.context import Context
from piet.ops import Add, Divide, Duplicate, Init, Multiply, Op, Pointer, Push, Resize, Substract


def test_ops_purity():
    class DummyOp(Op):
        def _call(self, context: Context) -> Context:
            context.stack = [18]
            context.value = 32
            return context

    op = DummyOp()

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


def test_str():
    @dataclass
    class DummyOp(Op):
        c: int
        a: str
        b: int

        def _call(self, context: Context) -> Context:
            return context

    op = DummyOp(b=1, c=2, a='e')

    assert str(op) == "DummyOp 2 'e' 1"


@pytest.mark.parametrize('op,expected_cost', [
    (Init(), 1), (Resize(1), 0), (Resize(2), 1), (Resize(3), 2),
    (Push(), 1), (Duplicate(), 1), (Add(), 1), (Multiply(), 1)
])
def test_cost(op, expected_cost):
    assert op._cost == expected_cost


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
    with pytest.raises(ValueError, match='Invalid non-positive resize value'):
        print(Resize(0))


def test_resize_negative_value():
    with pytest.raises(ValueError, match='Invalid non-positive resize value'):
        print(Resize(-4))


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


def test_substract():
    op = Substract()
    context = Context(stack=[1, 5, 2])
    expected_context = Context(stack=[1, 3])
    assert op(context) == expected_context


def test_multiply():
    op = Multiply()
    context = Context(stack=[1, 2, 3, 4])
    expected_context = Context(stack=[1, 2, 12])
    assert op(context) == expected_context


def test_divide():
    op = Divide()
    context = Context(stack=[1, 20, 3])
    expected_context = Context(stack=[1, 6])
    assert op(context) == expected_context


def test_pointer():
    op = Pointer()
    context = Context(stack=[1, 2, 3], value=4, dp=1)
    expected_context = Context(stack=[1, 2, 3], value=1, dp=5)
    assert op(context) == expected_context


def test_pointer_null_value():
    op = Pointer()
    context = Context()
    with pytest.raises(RuntimeError, match='Invalid non-positive pointer value'):
        print(op(context))


def test_pointer_negative_value():
    op = Pointer()
    context = Context(value=-4)
    with pytest.raises(RuntimeError, match='Invalid non-positive pointer value'):
        print(op(context))
