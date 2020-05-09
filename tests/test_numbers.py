from pathlib import Path

import pytest

from hilbertpiet.context import Context
from hilbertpiet.numbers import PushNumber, UnaryNumberTree


@pytest.mark.parametrize('tree,n', [
    (UnaryNumberTree(1), 1),
    (UnaryNumberTree(2), 2),
    (UnaryNumberTree(3), 3),
    (UnaryNumberTree(16) + UnaryNumberTree(4), 20),
    (UnaryNumberTree(16) - UnaryNumberTree(4), 12),
    (UnaryNumberTree(16) * UnaryNumberTree(4), 64),
    (UnaryNumberTree(20) // UnaryNumberTree(3), 6),
    (UnaryNumberTree(3) ** UnaryNumberTree(4), 81)
])
def test_number_tree_consistency(tree, n):
    assert tree.n == n
    assert tree(Context(value=1)).stack == [n]


@pytest.mark.parametrize('tree,expected', [
    (UnaryNumberTree(1), '1'),
    (UnaryNumberTree(2), '2'),
    (UnaryNumberTree(3), '3'),
    (UnaryNumberTree(16) + UnaryNumberTree(4), '16 + 4'),
    (UnaryNumberTree(16) - UnaryNumberTree(4), '16 - 4'),
    (UnaryNumberTree(16) * UnaryNumberTree(4), '16 * 4'),
    (UnaryNumberTree(20) // UnaryNumberTree(3), '20 // 3'),
    (UnaryNumberTree(3) ** UnaryNumberTree(4), '3 ** 4')
])
def test_number_tree_str(tree, expected):
    assert str(tree) == expected


@pytest.mark.parametrize('tree,expected', [
    (UnaryNumberTree(1), 1),
    (UnaryNumberTree(2), 2),
    (UnaryNumberTree(3), 3),
    (UnaryNumberTree(16) + UnaryNumberTree(4), 16 + 4 + 1),
    (UnaryNumberTree(16) - UnaryNumberTree(4), 16 + 4 + 1),
    (UnaryNumberTree(16) * UnaryNumberTree(4), 16 + 4 + 1),
    (UnaryNumberTree(20) // UnaryNumberTree(3), 20 + 3 + 1),
    (UnaryNumberTree(3) ** UnaryNumberTree(4), 3 + 2 * (4 - 1))
])
def test_number_tree_cost(tree, expected):
    assert tree._cost == expected


def test_push_number():
    MODULE_ROOT: Path = Path(__file__).parent.parent / 'hilbertpiet'
    numbers_filepath = MODULE_ROOT / 'data' / 'numbers.pkl'

    PushNumber.load_numbers(numbers_filepath)
    for n in range(1, 1000):
        number = PushNumber(n)
        assert number(Context(value=1)).stack == [n]
        assert number._cost == number._tree._cost
        assert eval(PushNumber(n).decomposition) == n
