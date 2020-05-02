import pytest
from pathlib import Path

from piet.context import Context
from piet.numbers import PushNumber, UnaryNumberAst


def assert_consistent_number(number: UnaryNumberAst, n: int):
    assert number.n == n
    assert number(Context()).stack == [n]


@pytest.mark.parametrize('n', [1, 2, 3, 5])
def test_unary(n):
    assert_consistent_number(UnaryNumberAst(n), n)


@pytest.mark.parametrize('n', [1, 2, 3, 5])
def test_unary_cost(n):
    assert UnaryNumberAst(n)._cost == (n - 1) + 1


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


def test_add_cost():
    n1, n2 = 16, 4
    assert (UnaryNumberAst(n1) + UnaryNumberAst(n2))._cost == n1 + n2 + 1


def test_add_str():
    n1, n2 = 16, 4
    assert str(UnaryNumberAst(n1) + UnaryNumberAst(n2)) == f'{n1} + {n2}'


def test_sub():
    n1, n2 = 16, 4
    expected = 12

    number = UnaryNumberAst(n1) - UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) - UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_sub_cost():
    n1, n2 = 16, 4
    assert (UnaryNumberAst(n1) - UnaryNumberAst(n2))._cost == n1 + n2 + 1


def test_sub_str():
    n1, n2 = 16, 4
    assert str(UnaryNumberAst(n1) - UnaryNumberAst(n2)) == f'{n1} - {n2}'


def test_mul():
    n1, n2 = 16, 4
    expected = 64

    number = UnaryNumberAst(n1) * UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) * UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_mul_cost():
    n1, n2 = 16, 4
    assert (UnaryNumberAst(n1) * UnaryNumberAst(n2))._cost == n1 + n2 + 1


def test_mult_str():
    n1, n2 = 16, 4
    assert str(UnaryNumberAst(n1) * UnaryNumberAst(n2)) == f'{n1} * {n2}'


def test_div():
    n1, n2 = 20, 3
    expected = 6

    number = UnaryNumberAst(n1) // UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) // UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_div_cost():
    n1, n2 = 20, 3
    assert (UnaryNumberAst(n1) // UnaryNumberAst(n2))._cost == n1 + n2 + 1


def test_div_str():
    n1, n2 = 20, 3
    assert str(UnaryNumberAst(n1) // UnaryNumberAst(n2)) == f'{n1} // {n2}'


def test_pow():
    n1, n2 = 3, 4
    expected = 81

    number = UnaryNumberAst(n1) ** UnaryNumberAst(n2)
    assert_consistent_number(number, expected)

    number = UnaryNumberAst(n1) ** UnaryNumberAst(n2)
    assert_consistent_number(number, expected)


def test_pow_cost():
    n1, n2 = 3, 4
    assert (UnaryNumberAst(n1) ** UnaryNumberAst(n2))._cost == n1 + 2 * (n2 - 1)


def test_pow_str():
    n1, n2 = 3, 4
    assert str(UnaryNumberAst(n1) ** UnaryNumberAst(n2)) == f'{n1} ** {n2}'


def test_push_number():
    MODULE_ROOT: Path = Path(__file__).parent.parent / 'piet'
    numbers_filepath = MODULE_ROOT / 'data' / 'numbers.pkl'

    PushNumber.load_numbers(numbers_filepath)
    for n in range(1, 10000):
        number = PushNumber(n)
        assert_consistent_number(number, n)
        assert number._cost == number._ast._cost
        assert eval(PushNumber(n).decomposition) == n
