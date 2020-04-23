import abc

from piet.context import Context
from piet.ops import Op, Push, Resize


class Macro(Op):
    def _call(self, context: Context) -> Context:
        for op in self.ops:
            context = op(context)
        return context

    @property
    @abc.abstractmethod
    def ops(self):
        raise NotImplementedError


class PushVal(Macro):
    def __init__(self, value: int):
        self.value = value

    @property
    def ops(self):
        return [Resize(self.value), Push()]