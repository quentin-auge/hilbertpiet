import abc
import operator
from copy import deepcopy
from dataclasses import dataclass, fields

from piet.context import Context


def purify_call(call):
    def wrapper(self, context) -> Context:
        new_context = deepcopy(context)
        return call(self, new_context)

    return wrapper


@dataclass(eq=False)
class Op:
    @purify_call
    def __call__(self, context: Context) -> Context:
        return self._call(context)

    @abc.abstractmethod
    def _call(self, context: Context) -> Context:
        raise NotImplementedError

    @property
    def _cost(self):
        return 1

    def __str__(self):
        cls = self.__class__.__name__

        params = []
        for param in fields(self):
            params.append(getattr(self, param.name))
        params = ' '.join(map(repr, params))

        return f'{cls} {params}'


class Init(Op):
    def _call(self, context: Context) -> Context:
        if context != Context():
            raise RuntimeError(f'Invalid non-empty context: "{context}"')

        context.value = 1
        return context


@dataclass(eq=False)
class Resize(Op):
    value: int

    def __init__(self, value: int):
        if value <= 0:
            raise ValueError(f'Invalid non-positive resize value {value}')
        self.value = value

    @property
    def _cost(self):
        return self.value - 1

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


class Duplicate(Op):
    def _call(self, context: Context) -> Context:
        x = context.stack.pop()
        context.stack.extend([x, x])
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


class Multiply(BinaryOp):
    binary_op = operator.mul
