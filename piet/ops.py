import operator
from copy import deepcopy

from piet.context import Context


class Op:
    pass


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
