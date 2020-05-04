import abc
import operator
from copy import deepcopy
from dataclasses import dataclass, fields

from piet.context import Context


def purify_call(call):
    """
    Transform an operation call that mutates a context into a pure function that creates
    a new context (pure function).
    """

    def wrapper(self, context) -> Context:
        new_context = deepcopy(context)
        return call(self, new_context)

    return wrapper


@dataclass(eq=False)
class Op:
    """
    A piet operation. Identifies with a codel, most of the time.
    """

    @purify_call
    def __call__(self, context: Context) -> Context:

        context = self._call(context)

        # Assume using Resize operation is the only way to set codel size
        if not isinstance(self, Resize):
            # Hence, all other operations are codels of size 1
            context.value = 1

        context.update_position(steps=self.size)

        return context

    @abc.abstractmethod
    def _call(self, context: Context) -> Context:
        raise NotImplementedError

    @property
    def size(self):
        """
        Size of equivalent codel.
        """
        return 1

    def __str__(self):
        cls = self.__class__.__name__

        params = []
        for param in fields(self):
            params.append(getattr(self, param.name))
        params = ' '.join(map(repr, params))

        return f'{cls} {params}'


class Init(Op):
    """
    First operation/codel of the program.

    Notes:
        Requires input context to be empty, for good measure.
    """

    def _call(self, context: Context) -> Context:
        if context != Context():
            raise RuntimeError(f'Invalid non-empty context: "{context}"')

        context.value = 1
        return context


@dataclass(eq=False)
class Resize(Op):
    """
    Sets the size of the previous codel and memorizes it as context value for the next operation.

    Notes:
        Not a real codel. Runtime knows how to handle it.
        Checks context value is positive. Null/negative codel sizes make no sense.
    """

    value: int

    def __init__(self, value: int):
        if value <= 0:
            raise ValueError(f'Invalid non-positive resize value {value}')
        self.value = value

    @property
    def size(self):
        return self.value - 1

    def _call(self, context: Context) -> Context:
        if context.value != 1:
            raise RuntimeError(f"Can't set resize value {self.value} "
                               f"over non-unitary resize value {context.value}")

        context.value = self.value
        return context


class Push(Op):
    """
    Push the context value (i.e. the size of the previous codel) to the stack.
    """

    def _call(self, context: Context) -> Context:
        if context.value <= 0:
            raise RuntimeError(f'Invalid non-positive push value {context.value}')

        context.stack.append(context.value)
        context.value = 1
        return context


class Duplicate(Op):
    """
    Pushes a copy of the top value on the stack on to the stack.
    """

    def _call(self, context: Context) -> Context:
        x = context.stack.pop()
        context.stack.extend([x, x])
        return context


class BinaryOp(Op):
    """
    Convenience class for factorizing binary stack operations.
    """

    binary_op = None

    def _call(self, context: Context) -> Context:
        stack = context.stack
        b, a = stack.pop(), stack.pop()
        result = self.binary_op(a, b)
        stack.append(result)
        return context


class Add(BinaryOp):
    """
    Pop the top two values off the stack, add them, and push the result back on the stack.
    """
    binary_op = operator.add


class Substract(BinaryOp):
    """
    Pop the top two values off the stack, calculate the second top value minus the top value,
    and push the result back on the stack.
    """
    binary_op = operator.sub


class Multiply(BinaryOp):
    """
    Pop the top two values off the stack, multiply them, and push the result back on the stack.
    """
    binary_op = operator.mul


class Divide(BinaryOp):
    """
    Pop the top two values off the stack, calculate the integer division of the second top value
    by the top value, and push the result back on the stack.
    """
    binary_op = operator.floordiv


class Pointer(Op):
    """
    Pop the top value off the stack and rotate the directional pointer by 90° clockwise that many
    steps (anticlockwise if negative).
    """

    def _call(self, context: Context) -> Context:
        context.rotate_dp(steps=context.stack.pop())
        return context
