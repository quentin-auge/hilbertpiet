import abc
from dataclasses import dataclass
from typing import List

from hilbertpiet.context import Context
from hilbertpiet.ops import Extend, Op


@dataclass(eq=False)
class Macro(Op):
    """
    Represents a list of Piet operations to be executed in sequence.
    """

    def __call__(self, context: Context) -> Context:
        for op in self.ops:
            context = op(context)
        return context

    @property
    def expanded_ops(self) -> List[Op]:
        """
        Recursively get the primitive operations (of type :class:`hilbertpiet.ops.Op`)
        represented by the macro.
        """

        expanded_ops = []
        for op in self.ops:
            if isinstance(op, Macro):
                expanded_ops += op.expanded_ops
            else:
                expanded_ops += [op]
        return expanded_ops

    @property
    def size(self) -> int:
        return sum(op.size for op in self.ops)

    @property
    @abc.abstractmethod
    def ops(self) -> List[Op]:
        raise NotImplementedError


@dataclass
class Resize(Macro):
    """
    Sets the size of the previous codel and memorizes it as context value for the next operation.

    Notes:
        Checks context value is positive. Null/negative codel sizes make no sense.
    """

    value: int

    def __init__(self, value: int):
        if value <= 1:
            raise ValueError(f'Invalid non-positive resize value {value}')
        self.value = value

    @property
    def ops(self) -> List[Op]:
        return [Extend() for _ in range(self.value - 1)]

    def __call__(self, context: Context) -> Context:
        if context.value != 1:
            raise RuntimeError(f"Can't set resize value {self.value} "
                               f"over non-unitary resize value {context.value}")
        return super().__call__(context)
