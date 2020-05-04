from copy import deepcopy

import pytest

from piet.context import Context


@pytest.mark.parametrize('invalid_dp', [0, 2, 0j, 2j, 1 + 1j])
def test_init_invalid_dp(invalid_dp):
    with pytest.raises(ValueError, match='Invalid dp value'):
        print(Context(dp=invalid_dp))


def test_str():
    c = Context(stack=[1, 2, 3], position=5 + 8j, value=4)
    assert str(c) == '[1, 2, 3] 4 (5+8j) 🡺'


@pytest.mark.parametrize('dp,expected_str_dp', [(1, '🡺'), (1j, '🡻'), (-1, '🡸'), (-1j, '🡹')])
def test_str_dp(dp, expected_str_dp):
    c = Context(dp=dp)
    assert str(c) == f'[] 0 0j {expected_str_dp}'


@pytest.mark.parametrize('dp', [1, 1j, -1, -1j])
@pytest.mark.parametrize('steps', list(range(-4, 5)))
def test_update_position(dp, steps):
    original_position = 3 + 2j

    context = Context(position=original_position, dp=dp)
    context.update_position(steps=steps)

    assert context.position == original_position + steps * context.dp


@pytest.mark.parametrize('dp', [1, 1j, -1, -1j])
@pytest.mark.parametrize('steps', list(range(-4, 5)))
def test_rotate(dp, steps):
    dp_values = [1, 1j, -1, -1j]
    dp_index = dp_values.index(dp)
    expected_dp_index = (dp_index + steps) % len(dp_values)
    expected_dp = dp_values[expected_dp_index]

    context = Context(dp=dp)
    context.rotate_dp(steps=steps)

    assert context.dp == expected_dp


def test_deepcopy():
    c1 = Context(stack=[1, 2, 3], value=4, position=5 + 8j, dp=1j)
    c2 = deepcopy(c1)

    assert c1 == c2
    assert c1.stack is not c2.stack
