from dataclasses import dataclass

import mock
import pytest

from hilbertpiet.context import Context
from hilbertpiet.ops import Add, Divide, Duplicate, Init, Multiply, Op
from hilbertpiet.ops import OutChar, OutNumber, Pointer, Pop, Push, Resize, Substract


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
    (Init(), 1),
    (Resize(2), 1), (Resize(3), 2), (Resize(4), 3), (Resize(10), 9),
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
def test_set_unitary_context_value(op):
    context = Context(stack=[2, 20, 3], value=7)
    assert context.value == 7

    context = op(context)
    assert context.value == 1


@pytest.mark.parametrize('op', [Pop(), Duplicate(), Add(), Substract(), Multiply(), Divide()])
def test_incremented_context_position(op):
    with mock.patch.object(Context, 'update_position') as mock_update_position:
        op(Context(stack=[2, 20, 3]))
        mock_update_position.assert_called_with(steps=1)


@pytest.mark.parametrize('op', [Pop(), Duplicate(), Add(), Substract(), Multiply(), Divide()])
def test_untouched_context_dp(op):
    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        op(Context(stack=[2, 20, 3]))
        mock_rotate_dp.assert_not_called()


@pytest.mark.parametrize('op', [Pop(), Duplicate(), Add(), Substract(), Multiply(), Divide()])
def test_untouched_context_output(op):
    context = Context(stack=[2, 20, 3], output='toto')
    context = op(context)
    assert context.output == 'toto'


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


@pytest.mark.parametrize('value', [2, 3, 4, 10])
def test_resize(value):
    op = Resize(value)

    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        with mock.patch.object(Context, 'update_position') as mock_update_position:
            context = Context(stack=[2, 20, 3], value=1, output='toto')

            context = op(context)

            assert context.stack == [2, 20, 3]
            assert context.value == value
            mock_rotate_dp.assert_not_called()
            mock_update_position.assert_called_with(steps=value - 1)
            assert context.output == 'toto'


@pytest.mark.parametrize('size', [-4, 0, 1])
def test_resize_invalid_size(size):
    with pytest.raises(ValueError, match='Invalid non-positive resize value'):
        print(Resize(size))


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
            context = Context(stack=[2, 20, 3], value=value, output='toto')

            context = op(context)

            assert context.stack == [2, 20, 3, value]
            assert context.value == 1
            mock_rotate_dp.assert_not_called()
            mock_update_position.assert_called_with(steps=1)
            assert context.output == 'toto'


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
            context = Context(stack=[20, 3, stack_value], output='toto')

            context = op(context)

            assert context.stack == [20, 3]
            assert context.value == 1
            mock_rotate_dp.assert_called_with(steps=stack_value)
            mock_update_position.assert_called_with(steps=1)
            assert context.output == 'toto'


@pytest.mark.parametrize('op', [
    pytest.param(OutNumber(), id='OutNumber'),
    pytest.param(OutChar(), id='OutChar')
])
def test_out_number(op):
    with mock.patch.object(Context, 'rotate_dp') as mock_rotate_dp:
        with mock.patch.object(Context, 'update_position') as mock_update_position:
            context = Context(stack=[20, 3, 112, 111, 110], output='output is ')

            context = op(context)
            context = op(context)
            context = op(context)

            assert context.stack == [20, 3]
            assert context.value == 1
            mock_rotate_dp.assert_not_called()
            mock_update_position.assert_called_with(steps=1)

            if isinstance(op, OutNumber):
                assert context.output == 'output is 110 111 112 '
            elif isinstance(op, OutChar):
                assert context.output == 'output is nop'
            else:
                raise NotImplementedError
