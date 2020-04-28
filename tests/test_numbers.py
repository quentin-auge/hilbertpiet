from pathlib import Path

import pytest

from piet.context import Context
from piet.numbers import PushNumber, UnaryNumberAst


def test_str():
    assert str(UnaryNumberAst(19)) == '19'


def assert_consistent_number(number: UnaryNumberAst, n: int):
    assert number.n == n
    assert number(Context()).stack == [n]


@pytest.mark.parametrize('n', [1, 2, 3, 5])
def test_unary(n):
    assert_consistent_number(UnaryNumberAst(n), n)


@pytest.mark.parametrize('n', [1, 2, 3, 5])
def test_unary_str(n):
    assert str(UnaryNumberAst(n)) == str(n)


def test_add():
    n1, n2 = 16, 4
    expected = 20

    number = UnaryNumberAst(n1) + UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) + UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_add_str():
    n1, n2 = 16, 4
    assert str(UnaryNumberAst(n1) + UnaryNumberAst(n2)) == '16 + 4'


def test_mul():
    n1, n2 = 16, 4
    expected = 64

    number = UnaryNumberAst(n1) * UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) * UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_mult_str():
    n1, n2 = 16, 4
    assert str(UnaryNumberAst(n1) * UnaryNumberAst(n2)) == '16 * 4'


def test_pow():
    n1, n2 = 3, 4
    expected = 81

    number = UnaryNumberAst(n1) ** UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) ** UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_pow_str():
    n1, n2 = 3, 4
    assert str(UnaryNumberAst(n1) ** UnaryNumberAst(n2)) == '3 ** 4'


def test_numbers_consistency():
    MODULE_ROOT: Path = Path(__file__).parent.parent / 'piet'
    numbers_filepath = MODULE_ROOT / 'piet_numbers.pkl'

    PushNumber.load_numbers(numbers_filepath)
    for n in range(1, 131):
        assert eval(PushNumber(n).decomposition) == n
