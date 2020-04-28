from __future__ import annotations

import abc
import operator
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List

from piet.macros import Macro
from piet.ops import Add, Duplicate, Multiply, Op, Push, Resize


@dataclass(eq=False)
class PushNumber(Macro):
    n: int

    __asts = {}

    @classmethod
    def load_numbers(cls, filepath: Path):
        with filepath.open('rb') as f:
            cls.__asts = pickle.load(f)

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
