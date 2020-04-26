import abc

from piet.context import Context
from piet.ops import Op


class Macro(Op):
    def _call(self, context: Context) -> Context:
        for op in self.ops:
            context = op(context)
        return context

    @property
    @abc.abstractmethod
    def ops(self):
        raise NotImplementedError
