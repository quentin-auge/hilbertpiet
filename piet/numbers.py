from __future__ import annotations

import abc
import operator
import pickle
from dataclasses import dataclass
from math import log, sqrt
from pathlib import Path
from typing import Dict, List

from piet.macros import Macro
from piet.ops import Add, Duplicate, Multiply, Op, Push, Resize


@dataclass(eq=False)
class PushNumber(Macro):
    n: int

    __asts = {}

    @classmethod
    def load_numbers(cls, filepath: Path):
        cls.__asts = PushNumberOptimizer.load(filepath)

    def __init__(self, n: int):
        self.n = n
        self._ast = self.__asts.get(n, UnaryNumberAst(n))

    @property
    def ops(self) -> List[Op]:
        return [self._ast]

    @property
    def decomposition(self) -> str:
        return str(self._ast)


class BaseNumberAst(Macro):

    def __init__(self, n: int):
        self.n = n

    @property
    @abc.abstractmethod
    def ops(self) -> List[Op]:
        raise NotImplementedError

    def __add__(self, other: BaseNumberAst) -> BaseNumberAst:
        return AddNumberAst(self, other)

    def __mul__(self, other: BaseNumberAst) -> BaseNumberAst:
        return MultNumberAst(self, other)

    def __pow__(self, other: BaseNumberAst) -> BaseNumberAst:
        return PowNumberAst(self, other)

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


class AddNumberAst(BinaryNumberAst):
    _binary_op = operator.add
    _binary_op_str = '+'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Add()]

    @property
    def _precedence(self) -> int:
        return 1


class MultNumberAst(BinaryNumberAst):
    _binary_op = operator.mul
    _binary_op_str = '*'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Multiply()]

    @property
    def _precedence(self) -> int:
        return 2


class PowNumberAst(BinaryNumberAst):
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


@dataclass
class PushNumberOptimizer:
    def __init__(self, max_num: int):
        self.max_num = max_num
        self.nums = {n: PushNumber(n) for n in range(1, max_num + 1)}

    def _optimize_add(self):
        for i in range(2, self.max_num - 2 + 1):
            for j in range(i, self.max_num - i + 1):
                self._step(operator.add, i, j)

    def _optimize_mult(self):
        for i in range(2, self.max_num // 2 + 1):
            for j in range(i, self.max_num // i + 1):
                self._step(operator.mul, i, j)

    def _optimize_pow(self):
        for i in range(2, int(sqrt(self.max_num) + 1)):
            for j in range(2, int(log(self.max_num, i) + 1)):
                self._step(operator.pow, i, j)

    def _step(self, binary_op, i: int, j: int):
        old_cost = self.nums[binary_op(i, j)]._cost

        candidate_ast = binary_op(self.nums[i]._ast, self.nums[j]._ast)
        new_cost = candidate_ast._cost

        if new_cost < old_cost:
            self.nums[binary_op(i, j)]._ast = candidate_ast

    @property
    def _cost(self):
        return sum(num._cost for num in self.nums.values())

    def save(self, out_filepath: Path):
        asts = {n: self.nums[n]._ast for n in self.nums}
        with out_filepath.open('wb') as f:
            pickle.dump(asts, f)

    @staticmethod
    def load(filepath: Path) -> Dict[int, BaseNumberAst]:
        with filepath.open('rb') as f:
            asts = pickle.load(f)
        return asts
