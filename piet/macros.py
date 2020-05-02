import abc
from typing import List

from piet.context import Context
from piet.ops import Op


class Macro(Op):
    def _call(self, context: Context) -> Context:
        for op in self.ops:
            context = op(context)
        return context

    @property
    def expanded_ops(self) -> List[Op]:
        expanded_ops = []
        for op in self.ops:
            if isinstance(op, Macro):
                expanded_ops += op.expanded_ops
            else:
                expanded_ops += [op]
        return expanded_ops


    @property
    def size(self):
        return sum(op.size for op in self.ops)

    @property
    @abc.abstractmethod
    def ops(self):
        raise NotImplementedError
