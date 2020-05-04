import abc
from typing import List

from piet.context import Context
from piet.ops import Op


class Macro(Op):
    """
    Represents a list of piet operations to be executed in sequence.
    """

    def _call(self, context: Context) -> Context:
        for op in self.ops:
            context = op(context)
        return context

    @property
    def expanded_ops(self) -> List[Op]:
        """
        Recursively get the primitive operations (of type :class:`piet.ops.Op`) represented by the
        macro.
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
