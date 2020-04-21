from copy import deepcopy

from piet.context import Context
from piet.ops import Add, Op


def test_ops_purity():
    class TestOp(Op):
        def _call(self, context: Context) -> Context:
            context.stack = [18]
            context.buffer = 32
            return context

    op = TestOp()

    context = Context(stack=[1, 2, 3], buffer=4)
    context1 = deepcopy(context)
    context2 = deepcopy(context)

    expected_context = Context(stack=[18], buffer=32)

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


def _test_op(op: Op, context: Context, expected_context: Context):
    original_context = deepcopy(context)

    # Assert operation correctness
    assert op(context) == expected_context

    # Ensure operation purity
    assert context == original_context


def test_add():
    context = Context(stack=[1, 2, 3])
    expected_context = Context(stack=[1, 5])
    _test_op(Add(), context, expected_context)
