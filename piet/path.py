from dataclasses import dataclass
from typing import List

from piet.context import Context
from piet.macros import Macro
from piet.ops import Duplicate, Op, Pointer, Pop, Push, Resize


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


@dataclass
class UTurn(Macro):
    """
    Perform a U-turn with codels. Stack remains the same.

    The operations are the following:
        * Setup:
            * Clockwise: 3 codels in the direction of dp
            * Anticlockwise: 3 codels in the direction of dp
            * Optional: `padding` extra codels if need be
        * First dp rotation: 1 codel
        * Move forward: 1 codel
        * Second dp rotation: 1 codel

    Notes:
        It is assumed the last codel before U-turn is anything but a `Resize` operation.
    """

    clockwise: bool
    padding: int = 0

    def __call__(self, context: Context) -> Context:

        if context.value != 1:
            raise RuntimeError(f'Invalid value before U-turn: {context.value}')

        return super().__call__(context)

    @property
    def ops(self) -> List[Op]:

        ops = [Push(), Duplicate(), Duplicate(), Pointer(), Pop(), Pointer()]

        if self.padding:
            ops.insert(1, Resize(self.padding + 1))

        if not self.clockwise:
            ops = [Resize(3)] + ops

        return ops
