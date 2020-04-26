from __future__ import annotations

import operator
from dataclasses import dataclass
from typing import List

from piet.macros import Macro
from piet.ops import Add, Duplicate, Multiply, Op, Push, Resize


@dataclass
class PushNumber(Macro):
    n: int

    def __init__(self, n: int):
        super().__init__()
        self.n = n
        self._ops = [Resize(n), Push()]

    def __str__(self):
        return str(self.n)

    @property
    def ops(self) -> List[Op]:
        return self._ops

    @property
    def pretty_decomposition(self) -> str:
        """
        Derive infix number expression from its postfix `Macro.expanded_ops` representation.
        """

        expanded_ops = self.expanded_ops

        stack = []

        last_str_op = None
        precedence = {None: 10, '+': 2, '*': 3}

        i = 0
        while i < len(expanded_ops):

            op = expanded_ops[i]

            if isinstance(op, Resize):
                stack.append(str(op.value))
                i += 1

            else:
                if isinstance(op, Add):
                    str_op = '+'
                elif isinstance(op, Multiply):
                    str_op = '*'
                else:
                    raise NotImplementedError

                y = stack.pop()
                x = stack.pop()

                if precedence[str_op] > precedence[last_str_op]:
                    expr = f'{x} {str_op} ({y})'
                else:
                    expr = f'{x} {str_op} {y}'

                stack.append(expr)

                last_str_op = str_op

            i += 1

        return stack.pop()

    def __add__(self, other: PushNumber) -> PushNumber:
        result = PushNumber(self.n + other.n)
        result._ops = [self, other, Add()]
        return result

    def __mul__(self, other: PushNumber) -> PushNumber:
        result = PushNumber(self.n * other.n)
        result._ops = [self, other, Multiply()]
        return result

    def __pow__(self, other: PushNumber) -> PushNumber:
        result = PushNumber(self.n ** other.n)
        result._ops = [self]
        result._ops += [Duplicate() for _ in range(1, other.n)]
        result._ops += [Multiply() for _ in range(1, other.n)]
        return result


def _compute_and_optimize(binary_op, i, j, nums):
    old_cost = nums[binary_op(i, j)]._cost

    candidate = binary_op(nums[i], nums[j])
    new_cost = candidate._cost

    if new_cost < old_cost:
        nums[binary_op(i, j)]._ops = candidate._ops


def optimize_add(nums, max_num):
    for i in range(2, max_num - 2 + 1):
        for j in range(i, max_num - i + 1):
            _compute_and_optimize(operator.add, i, j, nums)


def optimize_mult(nums, max_num):
    for i in range(2, max_num // 2 + 1):
        for j in range(i, max_num // i + 1):
            _compute_and_optimize(operator.mul, i, j, nums)


def get_total_cost(nums):
    return sum(num._cost if num else 0 for num in nums)


if __name__ == '__main__':
    max_num = 128
    nums = [None] + [PushNumber(i) for i in range(1, max_num + 1)]

    optimizations = [optimize_mult, optimize_add]

    print(f'Total cost = {get_total_cost(nums)}')

    for i, optimize in enumerate(optimizations, 1):
        print(f'Round {i}: {optimize.__name__}')
        optimize(nums, max_num)
        print(f'  Total cost = {get_total_cost(nums)}')

    for num in nums[1:]:
        print(f'{num} = {num.pretty_decomposition}')
