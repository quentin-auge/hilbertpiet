from __future__ import annotations

from dataclasses import dataclass

import abc
import operator
import pickle
from pathlib import Path
from typing import List

from piet.macros import Macro
from piet.ops import Add, Divide, Duplicate, Multiply, Op, Push, Resize, Substract


@dataclass(eq=False)
class PushNumber(Macro):
    """
    Push a given number on top of the context stack.

    Attributes:
        n: the produced number
    """

    n: int

    # Tree representation of a given set of numbers
    __trees = {}

    @classmethod
    def load_numbers(cls, filepath: Path):
        """
        Load tree representation of a set of numbers from a file.
        """
        with filepath.open('rb') as f:
            cls.__trees = pickle.load(f)

    def __init__(self, n: int):
        self.n = n
        self._tree = self.__trees.get(n, UnaryNumberTree(n))

    @property
    def _cost(self) -> int:
        """
        Cost of the number, i.e. number of codels required to produce it.
        """
        return self.size

    @property
    def ops(self) -> List[Op]:
        """
        Representation of the number as a tree of piet operations.
        """
        return [self._tree]

    @property
    def decomposition(self) -> str:
        """
        String representation of the tree as an arithmetic expression.
        """
        return str(self._tree)


@dataclass
class BaseNumberTree(Macro):
    """
    Base class for node of piet operations tree producing a given number on top of the context
    stack.

    Attributes:
        n: the number produced by the tree of operations
    """

    n: int

    def __init__(self, n: int):
        self.n = n

    @property
    @abc.abstractmethod
    def ops(self) -> List[Op]:
        raise NotImplementedError

    @property
    def _cost(self) -> int:
        """
        Cost of the number, i.e. number of codels required to produce it.
        """
        return self.size

    def __add__(self, other: BaseNumberTree) -> BaseNumberTree:
        return AddNumberTree(self, other)

    def __sub__(self, other: BaseNumberTree) -> BaseNumberTree:
        return SubNumberTree(self, other)

    def __mul__(self, other: BaseNumberTree) -> BaseNumberTree:
        return MultNumberTree(self, other)

    def __floordiv__(self, other: BaseNumberTree) -> BaseNumberTree:
        return DivNumberTree(self, other)

    def __pow__(self, other: BaseNumberTree) -> BaseNumberTree:
        return PowNumberTree(self, other)

    @abc.abstractmethod
    def __str__(self):
        """
        String representation of the tree as an arithmetic expression.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _precedence(self) -> int:
        raise NotImplementedError


@dataclass(eq=False)
class UnaryNumberTree(BaseNumberTree):
    """
    Leaf node of number tree, representing a number in the dumbest way possible
    (resize previous codel + push).

    Notes:
        Only valid for positive numbers.
    """

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
class BinaryNumberTree(BaseNumberTree):
    """
    Internal node of number tree, operating on its left and right child number nodes.
    """

    # Left child number node
    n1: BaseNumberTree
    # Left child number node
    n2: BaseNumberTree

    _binary_op = None
    _binary_op_str = None

    def __init__(self, n1: BaseNumberTree, n2: BaseNumberTree):
        self.n1, self.n2 = n1, n2
        super().__init__(self._binary_op(n1.n, n2.n))

    @property
    @abc.abstractmethod
    def ops(self) -> List[Op]:
        raise NotImplementedError

    def __str__(self):
        n1_str = str(self.n1)
        if self.n1._precedence <= self._precedence:
            n1_str = '(' + n1_str + ')'

        n2_str = str(self.n2)
        if self.n2._precedence <= self._precedence:
            n2_str = '(' + n2_str + ')'

        return f'{n1_str} {self._binary_op_str} {n2_str}'

    @property
    @abc.abstractmethod
    def _precedence(self) -> int:
        raise NotImplementedError


class AddNumberTree(BinaryNumberTree):
    _binary_op = operator.add
    _binary_op_str = '+'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Add()]

    @property
    def _precedence(self) -> int:
        return 1


class SubNumberTree(BinaryNumberTree):
    _binary_op = operator.sub
    _binary_op_str = '-'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Substract()]

    @property
    def _precedence(self) -> int:
        return 1


class MultNumberTree(BinaryNumberTree):
    _binary_op = operator.mul
    _binary_op_str = '*'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Multiply()]

    @property
    def _precedence(self) -> int:
        return 2


class DivNumberTree(BinaryNumberTree):
    _binary_op = operator.floordiv
    _binary_op_str = '//'

    @property
    def ops(self) -> List[Op]:
        return [self.n1, self.n2, Divide()]

    @property
    def _precedence(self) -> int:
        return 2


class PowNumberTree(BinaryNumberTree):
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
