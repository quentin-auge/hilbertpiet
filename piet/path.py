import abc
from dataclasses import dataclass
from typing import List, Literal, Union

from piet.context import Context
from piet.macros import Macro
from piet.ops import Add, Duplicate, Op, Pointer, Pop, Push, Resize


@dataclass(eq=False)
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

    @property
    @abc.abstractmethod
    def clockwise(self):
        raise NotImplementedError

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


@dataclass
class UTurnClockwise(UTurn):
    """
    Perform a clockwise U-turn with codels. Stack remains the same.
    """

    @property
    def clockwise(self):
        return True

    def __init__(self):
        super().__init__()


@dataclass
class UTurnAntiClockwise(UTurn):
    """
    Perform an anti-clockwise U-turn with codels. Stack remains the same.
    """

    @property
    def clockwise(self):
        return False

    def __init__(self):
        super().__init__()


@dataclass
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


def generate_path(n_iterations: int) -> str:
    """
    Generate path as a string of turtle instructions to trace a Hilbert curve II after a given
    number of iterations.

    Notes:
        Instructions are `F` (forward), `+` (turn right + forward), `-` (turn left + forward).
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


def map_path_u_turns(path: str) -> List[Union[Literal['C', 'A'], int]]:
    """
    Map first path character with 'I' (init), clockwise U-turns in path with 'C',
    anticlockwise U-turns with 'A', and remaining consecutive forwards with how many of them
    they are.

    Notes:
        Crash if transformation is impossible:
            * Can't map U-turns (not enough forwards to set up)
            * Single remaining forwards (can't map no-op to them)

    Examples:
        >>> _map_path_u_turns('FFFFFF+F+FFFFF-F-FFFFF')
        ['I', 2, 'C', 'A', 5]
    """

    # Integrate init in path (`I` character).
    path = 'I ' + path[1:]

    original_path = path

    # Integrate clockwise U-turns in path (`C` characters).
    # Make sure to replace the right number of path characters.
    expexted_setup_cost = 3
    assert UTurnClockwise().size == expexted_setup_cost + 3, 'Wrong UTurnClockwise cost'
    path = path.replace('F' * expexted_setup_cost + '+F+', ' C ')

    # Integrate anticlockwise U-turns in path (`A` characters).
    # Make sure to replace the right number of path characters.
    expexted_setup_cost = 5
    assert UTurnAntiClockwise().size == expexted_setup_cost + 3, 'Wrong UTurnAntiClockwise cost'
    path = path.replace('F' * expexted_setup_cost + '-F-', ' A ')

    path = path.strip()

    please_resize_path_msg = 'put in more iterations or stretch it'
    please_resize_path_msg += f'\n  Original path: {original_path}'
    please_resize_path_msg += f'\n  Transformed path: {path}'

    if '-' in path or '+' in path:
        # Unprocessed turns in resulting path means insufficient forwards quantity before
        # a U-turn to set it up.
        raise RuntimeError(f'Failed to replace all U-turns in path; {please_resize_path_msg}')

    # Remove empty spaces from path
    path = path.replace('  ', ' ')
    path = path.strip()

    transformed_path = path.split(' ')
    for i in range(len(transformed_path)):
        if transformed_path[i] not in ('I', 'C', 'A'):
            forwards_num = len(transformed_path[i])
            assert transformed_path[i] == 'F' * forwards_num, f'Ill-formed path: {path}'

            if forwards_num == 1:
                # No-ops (whose minimum length is 2) can't be mapped to single forwards.
                raise RuntimeError(
                    f'Generated single forwards in path; {please_resize_path_msg}')

            # Replace consecutive forwards with how many of them they are
            transformed_path[i] = forwards_num

    return transformed_path
