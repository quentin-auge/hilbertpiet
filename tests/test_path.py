import pytest

from piet.context import Context
from piet.path import UTurn, stretch_path

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


@pytest.mark.parametrize('dp', [1, 1j, -1, -1j])
@pytest.mark.parametrize('clockwise', [True, False])
@pytest.mark.parametrize('padding', list(range(4)))
def test_uturn(dp, clockwise, padding):
    original_stack = [2, 20, 3]
    original_position = 4 + 3j
    original_dp = dp
    context = Context(stack=[2, 20, 3], value=1, position=4 + 3j, dp=dp)

    # Initial position and codels number
    expected_position = original_position
    expected_size = 0

    # Position and codels number after clockwise / Anticlockwise U-turn setup
    if not clockwise:
        expected_position += 2 * dp
        expected_size += 2

    # Position and codels number after U-turn setup
    expected_position += 3 * dp
    expected_size += 3

    # Position and codels number after padding
    expected_position += padding * dp
    expected_size += padding

    # Position and codels number after U-turn
    expected_position += 2 * dp * (1j if clockwise else -1j) - dp
    expected_size += 3

    # Perform U-turn
    op = UTurn(clockwise, padding)
    context = op(context)

    # Test resulting context
    assert op.size == expected_size

    assert context.stack == original_stack
    assert context.value == 1
    assert context.value == 1
    assert context.position == expected_position

    assert context.dp == -original_dp


def test_uturn_over_invalid_value():
    context = Context(value=3)
    op = UTurn(clockwise=True)
    with pytest.raises(RuntimeError, match='Invalid value before U-turn'):
        print(op(context))
