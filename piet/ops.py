import abc
import operator
from copy import deepcopy

from piet.context import Context


class Op:
    @abc.abstractmethod
    def __call__(self, context: Context) -> Context:
        raise NotImplementedError

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __str__(self):
        return self.__class__.__name__


def purify_call(call):
    def wrapper(self, context) -> Context:
        new_context = deepcopy(context)
        return call(self, new_context)

    return wrapper


class BinaryOp(Op):
    binary_op = None

    @purify_call
    def __call__(self, context: Context) -> Context:
        stack = context.stack
        result = self.binary_op(stack.pop(), stack.pop())
        stack.append(result)
        return context


class Add(BinaryOp):
    binary_op = operator.add
