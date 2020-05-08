import abc
from dataclasses import dataclass
from typing import List, Literal, Union

from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Add, Duplicate, Op, Pointer, Pop, Push, Resize
from hilbertpiet.run import Program


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


def _stretch_path(path: str) -> str:
    """
    Stretch a path so that `n > 2` consecutive forwards (`F`) become  `5 * n + 2` consecutive
    forwards.
    """

    path += '$'
    i = 0
    stretched_path = ''
    n_forward = 0
    while i < len(path):
        c = path[i] if path[i] != '$' else ''
        if c != 'F':
            forwards = 'F' * (n_forward * 5 + 2) if n_forward != 1 else 'F'
            stretched_path += forwards + c
            n_forward = 0
        else:
            n_forward += 1
        i += 1

    return stretched_path


def generate_path(iterations: int) -> str:
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

    if iterations <= 0:
        return path

    for _ in range(iterations):
        path = ''.join(rules.get(c, c) for c in path)

    path = path.replace('X', '').replace('Y', '')

    return _stretch_path(path)


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
    expected_setup_cost = 3
    assert UTurnClockwise().size == expected_setup_cost + 3, 'Wrong UTurnClockwise cost'
    path = path.replace('F' * expected_setup_cost + '+F+', ' C ')

    # Integrate anticlockwise U-turns in path (`A` characters).
    # Make sure to replace the right number of path characters.
    expected_setup_cost = 5
    assert UTurnAntiClockwise().size == expected_setup_cost + 3, 'Wrong UTurnAntiClockwise cost'
    path = path.replace('F' * expected_setup_cost + '-F-', ' A ')

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


class NotEnoughSpace(BaseException):
    pass


def map_program_to_path(program: Program, path: List[Union[Literal['C', 'A'], int]]) -> Program:
    """
    Map a program (list of ops/macros) to empty slots in a path. Fill in the blanks with no-ops.

    Mind the following rules:
        * `NoOp(1)` is illegal
        * It is illegal to place a `Resize` operation before a no-op or U-turn

    Crash if path doesn't have enough space to accomodate the operations.
    """

    ops = program.expanded_ops

    mapped_ops = []
    i_path, i_ops = 1, 1

    while i_path < len(path):

        token = path[i_path]

        if token in ('C', 'A'):
            uturn_ops = {'C': UTurnClockwise(), 'A': UTurnAntiClockwise()}
            op = uturn_ops[token]
            mapped_ops.append(op)

        elif isinstance(token, int):
            available_size = token

            # Fill as many operation as possible in slot
            while i_ops < len(ops) and ops[i_ops].size <= available_size:
                mapped_ops.append(ops[i_ops])
                available_size -= ops[i_ops].size
                i_ops += 1

            # It is illegal to place a `Resize` operation before a no-op or U-turn.
            # `NoOp(1)` is illegal.
            while mapped_ops and isinstance(mapped_ops[-1], Resize) or available_size == 1:
                # Remove last operation from slot
                available_size += mapped_ops.pop().size
                i_ops -= 1

            # Fill blanks in slot with no-ops
            if available_size > 0:
                assert available_size > 1
                mapped_ops.append(NoOp(available_size))

        else:
            raise NotImplementedError

        i_path += 1

    if i_ops < len(ops):
        remaining = len(ops) - i_ops
        raise NotEnoughSpace(f'Not enough space in path; {remaining} remaining operations')

    mapped_program = Program(mapped_ops)

    return mapped_program
