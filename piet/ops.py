import operator
from copy import deepcopy

from piet.context import Context


class Op:
    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __str__(self):
        return self.__class__.__name__


class BinaryOp(Op):
    binary_op = None

    def __call__(self, context: Context) -> Context:
        new_context = deepcopy(context)

        stack = new_context.stack
        result = self.binary_op(stack.pop(), stack.pop())
        stack.append(result)

        return new_context


class Add(BinaryOp):
    binary_op = operator.add
