from __future__ import annotations

from dataclasses import dataclass
from typing import List

from piet.context import Context
from piet.macros import Macro
from piet.ops import Add, Multiply, Op, Push, Resize


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

    def __add__(self, other: PushNumber) -> PushNumber:
        result = PushNumber(self.n + other.n)
        result._ops = [self, other, Add()]
        return result

    def __mul__(self, other: PushNumber) -> PushNumber:
        result = PushNumber(self.n * other.n)
        result._ops = [self, other, Multiply()]
        return result


def optimize_mult(nums, max_num):
    for i in range(2, max_num // 2 + 1):
        for j in range(i, max_num // i + 1):

            old_cost = nums[i * j]._cost

            candidate = nums[i] * nums[j]
            new_cost = candidate._cost

            if new_cost < old_cost:
                nums[i * j]._ops = candidate._ops

def optimize_add(nums, max_num):
    for i in range(1, max_num - 2 + 1):
        for j in range(i, max_num - i + 1):

            old_cost = nums[i + j]._cost

            candidate = nums[i] + nums[j]
            new_cost = candidate._cost

            if new_cost < old_cost:
                nums[i + j]._ops = candidate._ops

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
        print(f'  {num} = {num.expand_ops()}, cost = {num._cost}')
