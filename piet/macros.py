import abc
from typing import List

from piet.context import Context
from piet.ops import Op


class Macro(Op):
    def _call(self, context: Context) -> Context:
        for op in self.ops:
            context = op(context)
        return context

    def expand_ops(self) -> List[Op]:
        expanded_ops = []
        for op in self.ops:
            if isinstance(op, Macro):
                expanded_ops += op.expand_ops()
            else:
                expanded_ops += [op]
        return expanded_ops


    @property
    def _cost(self):
        return sum(op._cost for op in self.ops)

    @property
    @abc.abstractmethod
    def ops(self):
        raise NotImplementedError
