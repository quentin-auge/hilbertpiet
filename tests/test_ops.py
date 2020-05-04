from copy import deepcopy
from dataclasses import dataclass

import mock
import pytest

from piet.context import Context
from piet.ops import Add, Divide, Duplicate, Init, Multiply, Op
from piet.ops import Pointer, Pop, Push, Resize, Substract


def test_ops_purity():
    class DummyOp(Op):
        def _call(self, context: Context) -> Context:
            context.stack = [4, 5, 6]
            return context

    op = DummyOp()

    context = Context(stack=[1, 2, 3])
    context1 = deepcopy(context)
    context2 = deepcopy(context)

    expected_mutated_context = Context(stack=[4, 5, 6])

    # `Op._call()` mutates the context
    mutated_context = op._call(context1)
    assert mutated_context is context1
    assert mutated_context.stack == [4, 5, 6]
    assert context1.stack == [4, 5, 6]

    # `Op.__call__()` creates a new context
    new_context = op(context2)
    assert new_context is not context2
    assert new_context.stack == [4, 5, 6]
    assert context2.stack == [1, 2, 3]


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


@pytest.mark.parametrize('op,expected_size', [
    (Init(), 1), (Resize(1), 0), (Resize(2), 1), (Resize(3), 2),
    (Push(), 1), (Pop(), 1), (Duplicate(), 1), (Add(), 1), (Substract(), 1),
    (Multiply(), 1), (Divide(), 1), (Pointer(), 1)
])
def test_size(op, expected_size):
    assert op.size == expected_size


@pytest.mark.parametrize('op,expected_stack', [
    (Pop(), [2, 20]),
    (Duplicate(), [2, 20, 3, 3]),
    (Add(), [2, 23]),
    (Substract(), [2, 17]),
    (Multiply(), [2, 60]),
    (Divide(), [2, 6])
])
def test_context_stack(op, expected_stack):
    context = op(Context(stack=[2, 20, 3]))
    assert context.stack == expected_stack


@pytest.mark.parametrize('op', [Pop(), Duplicate(), Add(), Substract(), Multiply(), Divide()])
def test_context_value(op):
    context = Context(stack=[2, 20, 3], value=7)
    assert context.value == 7

    context = op(context)
    assert context.value == 1


@pytest.mark.parametrize('op', [Pop(), Duplicate(), Add(), Substract(), Multiply(), Divide()])
def test_context_position(op):
    with mock.patch.object(Context, 'update_position') as mock_update_position:
        op(Context(stack=[2, 20, 3]))
        mock_update_position.assert_called_with(steps=1)


@pytest.mark.parametrize('op', [Pop(), Duplicate(), Add(), Substract(), Multiply(), Divide()])
def test_context_dp(op):
    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        op(Context(stack=[2, 20, 3]))
        mock_rotate_dp.assert_not_called()


def test_init():
    op = Init()
    context = Context()
    expected_context = Context(value=1, position=1)
    assert op(context) == expected_context


@pytest.mark.parametrize('context', [
    pytest.param(Context(stack=[1, 2, 3]), id='stack'),
    pytest.param(Context(value=4), id='value'),
    pytest.param(Context(position=3 + 2j), id='position'),
    pytest.param(Context(dp=-1j), id='dp')
])
def test_init_nonempty_context(context):
    op = Init()
    with pytest.raises(RuntimeError, match='Invalid non-empty context'):
        print(op(context))


@pytest.mark.parametrize('value', [1, 2, 3])
def test_resize(value):
    op = Resize(value)

    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        with mock.patch.object(Context, 'update_position') as mock_update_position:
            context = Context(stack=[2, 20, 3], value=1)

            context = op(context)

            assert context.stack == [2, 20, 3]
            assert context.value == value
            mock_rotate_dp.assert_not_called()
            mock_update_position.assert_called_with(steps=value - 1)


def test_resize_null_value():
    with pytest.raises(ValueError, match='Invalid non-positive resize value'):
        print(Resize(0))


def test_resize_negative_value():
    with pytest.raises(ValueError, match='Invalid non-positive resize value'):
        print(Resize(-4))


@pytest.mark.parametrize('initial_value', [0, 4])
def test_resize_over_non_unitary_value(initial_value):
    op = Resize(3)
    context = Context(value=initial_value)
    expected_msg = f"Can't set resize value 3 " \
                   f"over non-unitary resize value {context.value}"
    with pytest.raises(RuntimeError, match=expected_msg):
        print(op(context))


@pytest.mark.parametrize('value', [4, 5, 6])
def test_push(value):
    op = Push()

    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        with mock.patch.object(Context, 'update_position') as mock_update_position:
            context = Context(stack=[2, 20, 3], value=value)

            context = op(context)

            assert context.stack == [2, 20, 3, value]
            assert context.value == 1
            mock_rotate_dp.assert_not_called()
            mock_update_position.assert_called_with(steps=1)


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


@pytest.mark.parametrize('stack_value', list(range(-4, 5)))
def test_pointer(stack_value):
    op = Pointer()

    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        with mock.patch.object(Context, 'update_position') as mock_update_position:
            context = Context(stack=[20, 3, stack_value])

            context = op(context)

            assert context.stack == [20, 3]
            assert context.value == 1
            mock_rotate_dp.assert_called_with(steps=stack_value)
            mock_update_position.assert_called_with(steps=1)
