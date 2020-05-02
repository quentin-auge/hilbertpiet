from copy import deepcopy

import pytest

from piet.context import Context


def test_str():
    c = Context(stack=[1, 2, 3], value=4)
    assert str(c) == '[1, 2, 3] 4 🡺'


@pytest.mark.parametrize('dp,expected_str_dp',
                         [(0, '🡺'), (1, '🡻'), (2, '🡸'), (3, '🡹'),
                          (4, '🡺'), (5, '🡻'), (6, '🡸'), (7, '🡹'),
                          (-4, '🡺'), (-3, '🡻'), (-2, '🡸'), (-1, '🡹')])
def test_str_dp(dp, expected_str_dp):
    c = Context(dp=dp)
    assert str(c) == f'[] 0 {expected_str_dp}'


def test_deepcopy():
    c1 = Context(stack=[1, 2, 3], value=4, dp=2)
    c2 = deepcopy(c1)

    assert c1 == c2
    assert c1.stack is not c2.stack
