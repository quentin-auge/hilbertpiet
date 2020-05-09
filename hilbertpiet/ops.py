import abc
import operator
from dataclasses import dataclass, fields

from hilbertpiet.context import Context


@dataclass(eq=False)
class Op:
    """
    A Piet operation. Identifies with a codel, most of the time.
    """

    def __call__(self, context: Context) -> Context:

        context = self._call(context)

        # Assume using Extend operation is the only way to change codel size
        if not isinstance(self, Extend):
            # Hence, all other operations are codels of size 1
            context.value = 1

        context.update_position(steps=self.size)

        return context

    @abc.abstractmethod
    def _call(self, context: Context) -> Context:
        """
        Context transformation associated with the operation.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def color_change(self) -> complex:
        """
        Lightness (real part) and hue (imag part) change associated with the operation.
        """
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


@dataclass
class Init(Op):
    """
    First operation/codel of the program.

    Notes:
        Requires input context to be empty, for good measure.
    """

    def _call(self, context: Context) -> Context:
        if context != Context():
            raise RuntimeError(f'Invalid non-empty context: "{context}"')
        return context

    @property
    def color_change(self) -> complex:
        return 0 + 0j


@dataclass
class Extend(Op):
    """
    Increment the size of the previous codel and memorizes it as context value for the next
    operation.

    Notes:
        Not a real codel. Runtime knows how to handle it.
    """

    def _call(self, context: Context) -> Context:
        context.value += 1
        return context

    @property
    def color_change(self) -> complex:
        return 0 + 0j


@dataclass
class Push(Op):
    """
    Push the context value (i.e. the size of the previous codel) to the stack.
    """

    def _call(self, context: Context) -> Context:
        if context.value <= 0:
            raise RuntimeError(f'Invalid non-positive push value {context.value}')

        context.stack.append(context.value)
        return context

    @property
    def color_change(self) -> complex:
        return 1 + 0j


@dataclass
class Pop(Op):
    """
    Pop the top value off the stack and discard it.
    """

    def _call(self, context: Context) -> Context:
        context.stack.pop()
        return context

    @property
    def color_change(self) -> complex:
        return 2 + 0j


@dataclass
class Duplicate(Op):
    """
    Pushes a copy of the top value on the stack on to the stack.
    """

    def _call(self, context: Context) -> Context:
        x = context.stack.pop()
        context.stack.extend([x, x])
        return context

    @property
    def color_change(self) -> complex:
        return 0 + 4j


@dataclass(eq=False)
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


@dataclass
class Add(BinaryOp):
    """
    Pop the top two values off the stack, add them, and push the result back on the stack.
    """
    binary_op = operator.add

    @property
    def color_change(self) -> complex:
        return 0 + 1j


@dataclass
class Substract(BinaryOp):
    """
    Pop the top two values off the stack, calculate the second top value minus the top value,
    and push the result back on the stack.
    """
    binary_op = operator.sub

    @property
    def color_change(self) -> complex:
        return 1 + 1j


@dataclass
class Multiply(BinaryOp):
    """
    Pop the top two values off the stack, multiply them, and push the result back on the stack.
    """
    binary_op = operator.mul

    @property
    def color_change(self) -> complex:
        return 2 + 1j


@dataclass
class Divide(BinaryOp):
    """
    Pop the top two values off the stack, calculate the integer division of the second top value
    by the top value, and push the result back on the stack.
    """
    binary_op = operator.floordiv

    @property
    def color_change(self) -> complex:
        return 0 + 2j


@dataclass
class Pointer(Op):
    """
    Pop the top value off the stack and rotate the directional pointer by 90° clockwise that many
    steps (anticlockwise if negative).
    """

    def _call(self, context: Context) -> Context:
        context.rotate_dp(steps=context.stack.pop())
        return context

    @property
    def color_change(self) -> complex:
        return 1 + 3j


@dataclass
class OutNumber(Op):
    """
    Pop the top value off the stack and append it to output as number.
    """

    def _call(self, context: Context) -> Context:
        context.output += f'{context.stack.pop()} '
        return context

    @property
    def color_change(self) -> complex:
        return 1 + 5j


@dataclass
class OutChar(Op):
    """
    Pop the top value off the stack and append it to output as character.
    """

    def _call(self, context: Context) -> Context:
        context.output += chr(context.stack.pop())
        return context

    @property
    def color_change(self) -> complex:
        return 0 + 5j
