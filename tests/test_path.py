import pytest

from piet.context import Context
from piet.path import NoOp, UTurnAntiClockwise, UTurnClockwise, stretch_path

clockwise_params = [pytest.param(True, id='clockwise'), pytest.param(False, id='anticlockwise')]


@pytest.mark.parametrize('dp', [1, 1j, -1, -1j])
@pytest.mark.parametrize('clockwise', clockwise_params)
def test_uturn(dp, clockwise):
    original_stack = [2, 20, 3]
    original_position = 4 + 3j
    original_dp = dp
    context = Context(stack=[2, 20, 3], value=1, position=4 + 3j, dp=dp)

    # Initial position and codels number
    expected_position = original_position
    expected_size = 0

    # Position and codels number after U-turn setup
    expected_setup_cost = 3 if clockwise else 5
    expected_position += expected_setup_cost * dp
    expected_size += expected_setup_cost

    # Position and codels number after U-turn
    expected_position += 2 * dp * (1j if clockwise else -1j) - dp
    expected_size += 3

    # Perform U-turn
    op = UTurnClockwise() if clockwise else UTurnAntiClockwise()
    context = op(context)

    assert op.size == expected_size

    # Test resulting context

    assert context.stack == original_stack
    assert context.value == 1
    assert context.value == 1
    assert context.position == expected_position
    assert context.dp == -original_dp
    assert context.output == ''


@pytest.mark.parametrize('clockwise', clockwise_params)
def test_uturn_over_invalid_value(clockwise):
    context = Context(value=3)
    op = UTurnClockwise() if clockwise else UTurnAntiClockwise()
    with pytest.raises(RuntimeError, match='Invalid value before U-turn'):
        print(op(context))


@pytest.mark.parametrize('length', [2, 3, 4, 5])
def test_no_op(length):
    op = NoOp(length)

    context = Context(stack=[2, 20, 3], value=1, dp=1j)

    context = op(context)

    assert op.size == length
    assert context.stack == [2, 20, 3]
    assert context.value == 1
    assert context.dp == 1j
    assert context.output == ''


@pytest.mark.parametrize('length', [-1, 0, 1])
def test_no_op_invalid_length(length):
    with pytest.raises(ValueError, match='Invalid no-op length'):
        print(NoOp(length))


def test_no_op_over_invalid_value():
    context = Context(value=3)
    op = NoOp(2)
    with pytest.raises(RuntimeError, match='Invalid value before no-op'):
        print(op(context))


n_forwards_factors_params = [(n_forwards, factor)
                             for n_forwards in range(4)
                             for factor in range(1, 4)]


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_start_end(n_forwards, factor):
    path = 'F' * n_forwards

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = 'F' * expected_n_forwards

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_start(n_forwards, factor):
    path = '+' + 'F' * n_forwards

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = '+' + 'F' * expected_n_forwards

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_end(n_forwards, factor):
    path = 'F' * n_forwards + '+'

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = 'F' * expected_n_forwards + '+'

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_middle(n_forwards, factor):
    path = '+' + 'F' * n_forwards + '+'

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = '+' + 'F' * expected_n_forwards + '+'

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_mixed_middle(n_forwards, factor):
    path = '+' + 'F' * n_forwards * 2
    path += '-o-' + 'F' * n_forwards * 3
    path += '-p-' + 'F' * n_forwards + '+'

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = '+' + 'F' * n_forwards * 2 * factor
    expected_path += '-o-' + 'F' * n_forwards * 3 * factor
    expected_path += '-p-' + 'F' * expected_n_forwards + '+'

    assert stretch_path(path, factor) == expected_path
