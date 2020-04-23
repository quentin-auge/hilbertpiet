import abc
import operator
from copy import deepcopy

from piet.context import Context


def purify_call(call):
    def wrapper(self, context) -> Context:
        new_context = deepcopy(context)
        return call(self, new_context)

    return wrapper


class Op:
    @purify_call
    def __call__(self, context: Context) -> Context:
        return self._call(context)

    @abc.abstractmethod
    def _call(self, context: Context) -> Context:
        raise NotImplementedError

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __str__(self):
        return self.__class__.__name__


class Init(Op):
    def _call(self, context: Context) -> Context:
        if context != Context():
            raise RuntimeError(f'Invalid non-empty context: "{context}"')

        context.value = 1
        return context


class Resize(Op):
    def __init__(self, value: int):
        self.value = value

    def _call(self, context: Context) -> Context:
        context.value = self.value
        return context


class Push(Op):
    def _call(self, context: Context) -> Context:
        if context.value <= 0:
            raise RuntimeError(f'Invalid non-positive push value {context.value}')

        context.stack.append(context.value)
        context.value = 1
        return context


class BinaryOp(Op):
    binary_op = None

    def _call(self, context: Context) -> Context:
        stack = context.stack
        result = self.binary_op(stack.pop(), stack.pop())
        stack.append(result)
        return context


class Add(BinaryOp):
    binary_op = operator.add
