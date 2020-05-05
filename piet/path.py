from dataclasses import dataclass
from typing import List

from piet.context import Context
from piet.macros import Macro
from piet.ops import Add, Duplicate, Op, Pointer, Pop, Push, Resize


def generate_path(n_iterations: int) -> str:
    """
    Generate path as a string of turtle instructions to trace a Hilbert curve II after a given
    number of iterations.

    Notes:
        Instructions are `F` (forward), `+` (turn right), `-` (turn left).
        https://elc.github.io/posts/plotting-fractals-step-by-step-with-python/#hilbert-curve-ii.
    """

    # L-system rules for Hilbert curve II
    rules = {'X': 'XFYFX+F+YFXFY-F-XFYFX', 'Y': 'YFXFY-F-XFYFX+F+YFXFY'}
    path = 'X'

    if n_iterations <= 0:
        return path

    for _ in range(n_iterations):
        path = ''.join(rules.get(c, c) for c in path)

    path = path.replace('X', '').replace('Y', '')

    return path


def stretch_path(path: str, factor: int) -> str:
    """
    Stretch a path so that `n` consecutive forwards (`F`) become  `n * factor` consecutive forwards.
    """

    path += '$'
    i = 0
    stretched_path = ''
    n_forward = 0
    while i < len(path):
        c = path[i] if path[i] != '$' else ''
        if c != 'F':
            forwards = 'F' * n_forward * factor if n_forward != 1 else 'F'
            stretched_path += forwards + c
            n_forward = 0
        else:
            n_forward += 1
        i += 1

    return stretched_path


@dataclass(repr=False, eq=False)
class UTurn(Macro):
    """
    Perform a U-turn with codels. Stack remains the same.

    The operations are the following:
        * Setup:
            * Clockwise: 3 codels in the direction of dp
            * Anticlockwise: 5 codels in the direction of dp
        * First dp rotation: 1 codel
        * Move forward: 1 codel
        * Second dp rotation: 1 codel

    Notes:
        It is assumed the last codel before U-turn is anything but a `Resize` operation.
    """

    clockwise: bool

    def __call__(self, context: Context) -> Context:

        if context.value != 1:
            raise RuntimeError(f'Invalid value before U-turn: {context.value}')

        return super().__call__(context)

    @property
    def ops(self) -> List[Op]:

        ops = [Push(), Duplicate(), Duplicate(), Pointer(), Pop(), Pointer()]

        if not self.clockwise:
            ops = [Resize(3)] + ops

        return ops


@dataclass(eq=False)
class UTurnClockwise(UTurn):
    """
    Perform a clockwise U-turn with codels. Stack remains the same.
    """

    def __init__(self):
        super().__init__(clockwise=True)


@dataclass(eq=False)
class UTurnAntiClockwise(UTurn):
    """
    Perform an anti-clockwise U-turn with codels. Stack remains the same.
    """

    def __init__(self):
        super().__init__(clockwise=False)


@dataclass(eq=False)
class NoOp(Macro):
    """
    A given number of codels that ultimately don't touch either the stack or dp.

    Notes:
        It is assumed the last codel before U-turn is anything but a `Resize` operation.
    """

    length: int

    def __init__(self, length: int):
        if length <= 1:
            raise ValueError(f'Invalid no-op length: {length}')
        self.length = length

    def __call__(self, context: Context) -> Context:

        if context.value != 1:
            raise RuntimeError(f'Invalid value before no-op: {context.value}')

        return super().__call__(context)

    @property
    def ops(self) -> List[Op]:
        ops = [Push()]

        if self.length % 2 == 1:
            ops.append(Resize(2))

        ops += [Duplicate(), Add()] * (self.length // 2 - 1)

        ops.append(Pop())

        return ops
