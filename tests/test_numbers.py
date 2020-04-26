import pytest

from piet.context import Context
from piet.numbers import PushNumber


def test_str():
    assert str(PushNumber(19)) == '19'


def assert_consistent_number(number: PushNumber, n: int):
    assert number.n == n
    assert number(Context()).stack == [n]


@pytest.mark.parametrize('n', [1, 2, 3])
def test_default(n):
    assert_consistent_number(PushNumber(n), n)


def test_add():
    n1, n2 = 16, 4
    expected = 20

    number = PushNumber(n1) + PushNumber(n2)
    assert_consistent_number(number, expected)

    number = PushNumber(n1) + PushNumber(n2)
    assert_consistent_number(number, expected)


def test_mul():
    n1, n2 = 16, 4
    expected = 64

    number = PushNumber(n1) * PushNumber(n2)
    assert_consistent_number(number, expected)

    number = PushNumber(n1) * PushNumber(n2)
    assert_consistent_number(number, expected)
