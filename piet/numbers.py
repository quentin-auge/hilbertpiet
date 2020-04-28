from __future__ import annotations

import abc
import operator
from dataclasses import dataclass
from math import log, sqrt
from typing import List

from piet.macros import Macro
from piet.ops import Add, Duplicate, Multiply, Op, Push, Resize


class BaseNumberAst(Macro):

    def __init__(self, n: int):
        self.n = n

    @property
    @abc.abstractmethod
    def ops(self) -> List[Op]:
        raise NotImplementedError

    def __add__(self, other: BaseNumberAst) -> BaseNumberAst:
        return PushAddNumber(self, other)

    def __mul__(self, other: BaseNumberAst) -> BaseNumberAst:
        return PushMultNumber(self, other)

    def __pow__(self, other: BaseNumberAst) -> BaseNumberAst:
        return PushPowNumber(self, other)

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _precedence(self) -> int:
        raise NotImplementedError


@dataclass(eq=False)
class UnaryNumberAst(BaseNumberAst):
    n: int

    def __init__(self, n: int):
        super().__init__(n)

    @property
    def ops(self):
        return [Resize(self.n), Push()]

    def __str__(self):
        return str(self.n)

    @property
    def _precedence(self):
        return 10


@dataclass(eq=False)
class BinaryNumberAst(BaseNumberAst):
    n1: BaseNumberAst
    n2: BaseNumberAst

    _binary_op = None
    _binary_op_str = None

    def __init__(self, n1: BaseNumberAst, n2: BaseNumberAst):
        self.n1, self.n2 = n1, n2
        super().__init__(self._binary_op(n1.n, n2.n))

    @property
    @abc.abstractmethod
    def ops(self) -> List[Op]:
        raise NotImplementedError

    def __str__(self):
        n1_str = str(self.n1)
        if self.n1._precedence < self._precedence:
            n1_str = '(' + n1_str + ')'

        n2_str = str(self.n2)
        if self.n2._precedence < self._precedence:
            n2_str = '(' + n2_str + ')'

        return f'{n1_str} {self._binary_op_str} {n2_str}'

    @property
    @abc.abstractmethod
    def _precedence(self) -> int:
        raise NotImplementedError


class PushAddNumber(BinaryNumberAst):
    _binary_op = operator.add
    _binary_op_str = '+'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Add()]

    @property
    def _precedence(self) -> int:
        return 1


class PushMultNumber(BinaryNumberAst):
    _binary_op = operator.mul
    _binary_op_str = '*'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Multiply()]

    @property
    def _precedence(self) -> int:
        return 2


class PushPowNumber(BinaryNumberAst):
    _binary_op = operator.pow
    _binary_op_str = '**'

    @property
    def ops(self) -> List[Op]:
        ops = [self.n1]
        ops += [Duplicate() for _ in range(1, self.n2.n)]
        ops += [Multiply() for _ in range(1, self.n2.n)]
        return ops

    @property
    def _precedence(self) -> int:
        return 3


def _compute_and_optimize(binary_op, i, j, nums):
    old_cost = nums[binary_op(i, j)]._cost

    candidate = binary_op(nums[i], nums[j])
    new_cost = candidate._cost

    if new_cost < old_cost:
        nums[binary_op(i, j)] = candidate


def optimize_add(nums, max_num):
    for i in range(2, max_num - 2 + 1):
        for j in range(i, max_num - i + 1):
            _compute_and_optimize(operator.add, i, j, nums)


def optimize_mult(nums, max_num):
    for i in range(2, max_num // 2 + 1):
        for j in range(i, max_num // i + 1):
            _compute_and_optimize(operator.mul, i, j, nums)


def optimize_pow(nums, max_num):
    for i in range(2, int(sqrt(max_num) + 1)):
        for j in range(i, int(log(max_num, i) + 1)):
            _compute_and_optimize(operator.pow, i, j, nums)


def get_total_cost(nums):
    return sum(num._cost if num else 0 for num in nums)


if __name__ == '__main__':

    max_num = 128
    nums = [None] + [UnaryNumberAst(i) for i in range(1, max_num + 1)]

    optimizations = [optimize_pow, optimize_mult, optimize_add] * 3

    print(f'Total cost = {get_total_cost(nums)}')

    for i, optimize in enumerate(optimizations, 1):
        print(f'Round {i}: {optimize.__name__}')
        optimize(nums, max_num)
        print(f'  Total cost = {get_total_cost(nums)}')

    for num in nums[1:]:
        print(f'{num.n} = {num} = {repr(num)}, cost = {num._cost}')
