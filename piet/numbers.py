from __future__ import annotations

from dataclasses import dataclass
from typing import List

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
