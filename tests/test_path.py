import pytest

from hilbertpiet.context import Context
from hilbertpiet.macros import Resize
from hilbertpiet.ops import Extend, Init, Push
from hilbertpiet.path import NoOp, NotEnoughSpace, UTurnAntiClockwise, UTurnClockwise
from hilbertpiet.path import map_path_u_turns, map_program_to_path
from hilbertpiet.run import Program

clockwise_params = [pytest.param(True, id='clockwise'), pytest.param(False, id='anticlockwise')]


@pytest.mark.parametrize('dp', [1, 1j, -1, -1j])
@pytest.mark.parametrize('clockwise', clockwise_params)
def test_uturn(dp, clockwise):
    original_stack = [2, 20, 3]
    original_position = 4 + 3j
    original_dp = dp
    context = Context(stack=[2, 20, 3], value=1, position=4 + 3j, dp=dp)

    # Initial position and codels number
    expected_position = original_position
    expected_size = 0

    # Position and codels number after U-turn setup
    expected_setup_cost = 3 if clockwise else 5
    expected_position += expected_setup_cost * dp
    expected_size += expected_setup_cost

    # Position and codels number after U-turn
    expected_position += 2 * dp * (1j if clockwise else -1j) - dp
    expected_size += 3

    # Perform U-turn
    op = UTurnClockwise() if clockwise else UTurnAntiClockwise()
    context = op(context)

    assert op.size == expected_size

    # Test resulting context

    assert context.stack == original_stack
    assert context.value == 1
    assert context.value == 1
    assert context.position == expected_position
    assert context.dp == -original_dp
    assert context.output == ''


@pytest.mark.parametrize('clockwise', clockwise_params)
def test_uturn_over_invalid_value(clockwise):
    context = Context(value=3)
    op = UTurnClockwise() if clockwise else UTurnAntiClockwise()
    with pytest.raises(RuntimeError, match='Invalid value before U-turn'):
        print(op(context))


@pytest.mark.parametrize('length', [2, 3, 4, 5])
def test_no_op(length):
    op = NoOp(length)

    context = Context(stack=[2, 20, 3], value=1, dp=1j)

    context = op(context)

    assert op.size == length
    assert context.stack == [2, 20, 3]
    assert context.value == 1
    assert context.dp == 1j
    assert context.output == ''


@pytest.mark.parametrize('length', [-1, 0, 1])
def test_no_op_invalid_length(length):
    with pytest.raises(ValueError, match='Invalid no-op length'):
        print(NoOp(length))


def test_no_op_over_invalid_value():
    context = Context(value=3)
    op = NoOp(2)
    with pytest.raises(RuntimeError, match='Invalid value before no-op'):
        print(op(context))


@pytest.mark.parametrize('path,expected', [
    ('F', ['I']),
    ('FF', RuntimeError('Generated single forwards in path')),
    ('FFF', ['I', 2]),
    ('FFFFFF', ['I', 5]),
    ('FFFF+F+', ['I', 'C']),
    ('FFFFFFF+F+', ['I', 3, 'C']),
    ('FFF+F+', RuntimeError('Failed to replace all U-turns in path')),
    ('FFFFF+F+', RuntimeError('Generated single forwards in path')),
    ('FFFFFF-F-', ['I', 'A']),
    ('FFFFFFFFF-F-', ['I', 3, 'A']),
    ('FFFFF-F-', RuntimeError('Failed to replace all U-turns in path')),
    ('FFFFFFF-F-', RuntimeError('Generated single forwards in path')),
    ('FFFF+F+FFFFF-F-FFF+F+', ['I', 'C', 'A', 'C']),
    ('FFFF+F+FFFFFFF-F-FFFFFF+F+FF', ['I', 'C', 2, 'A', 3, 'C', 2]),
    ('FFFF+F+FFFFFF-F-FFFFFF+F+FF', RuntimeError('Generated single forwards in path')),
    ('FFFF+F+FFFF-F-FFF+F+FF', RuntimeError('Failed to replace all U-turns in path'))
])
def test_map_path_u_turns(path, expected):
    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=str(expected)):
            print(map_path_u_turns(path))
    else:
        assert map_path_u_turns(path) == expected


@pytest.mark.parametrize('path,ops,expected', [

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [],
        [Init(),
         NoOp(5), UTurnClockwise(),
         NoOp(6), UTurnAntiClockwise(),
         NoOp(7), UTurnClockwise(),
         NoOp(2)],
        id='no_resize'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(2), Push()],
        # All ops fit in first slot with 2 codels left
        [Init(),
         Push()] + [Extend()] * 1 + [Push(), NoOp(2), UTurnClockwise(),
         NoOp(6), UTurnAntiClockwise(),
         NoOp(7), UTurnClockwise(),
         NoOp(2)],
        id='resize_2'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(3), Push()],
        # All ops fit in first slot with 1 codel left -> illegal NoOp(1), carry last Push forward
        # First slot now ends with Resize -> illegal, carry Resize forward
        # Resize + Push fit in second slot with 3 codels left
        [Init(),
         Push(), NoOp(4), UTurnClockwise()] +
         [Extend()] * 2 + [Push(), NoOp(3), UTurnAntiClockwise(),
         NoOp(7), UTurnClockwise(),
         NoOp(2)],
        id='resize_3'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(4), Push()],
        # All ops fit in first slot with 0 codel left
        [Init(),
         Push()] + [Extend()] * 3 + [Push(), UTurnClockwise(),
         NoOp(6), UTurnAntiClockwise(),
         NoOp(7), UTurnClockwise(),
         NoOp(2)],
        id='resize_4'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(5), Push()],
        # Push + Resize fit in first slot, but last op is Resize -> illegal, move Resize forward
        # Resize + Push fit in second slot, with 1 codel left -> illegal NoOp(1), carry last Push
        #   forward
        # Second slot now ends with Resize -> illegal, carry Resize forward
        # Resize + Push fit in third slot, with 2 codels left
        [Init(),
         Push(), NoOp(4), UTurnClockwise(),
         NoOp(6), UTurnAntiClockwise()] +
         [Extend()] * 4 + [Push(), NoOp(2), UTurnClockwise(),
         NoOp(2)],
        id='resize_5'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(6), Push()],
        # Push fits in first slot with 4 codels left
        # Resize + Push fit in second slot with 0 codel left
        [Init(),
         Push(), NoOp(4), UTurnClockwise()] +
         [Extend()] * 5 + [Push(), UTurnAntiClockwise(),
         NoOp(7), UTurnClockwise(),
         NoOp(2)],
        id='resize_6'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(7), Push()],
        # Push fits in first slot with 4 codels left
        # Resize fits in second slot, but last op is Resize -> illegal, carry Resize forward
        # Resize + Push fit in second slot, with 0 codel left
        [Init(),
         Push(), NoOp(4), UTurnClockwise(),
         NoOp(6), UTurnAntiClockwise()] +
        [Extend()] * 6 + [Push(), UTurnClockwise(),
         NoOp(2)],
        id='resize_7'
    ),

    pytest.param(
        ['I', 5, 'C', 6, 'A', 7, 'C', 2],
        [Push(), Resize(8), Push()],
        # Push fits in first slot with 4 codels left
        # Resize does not fit in second slot
        # Resize fits in third slot, but last op is Resize -> illegal, move Resize forward
        # Resize does not fit in fourth spot -> ERROR, no space left
        NotEnoughSpace('Not enough space in path'),
        id='resize_8'
    )
])
def test_map_program_to_path(path, ops, expected):
    program = Program(ops)

    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=str(expected)):
            print(map_program_to_path(program, path))

    else:
        # Expect given output program ops
        mapped_program = map_program_to_path(program, path)
        assert mapped_program.ops == expected

        # Make sure initial and mapped ops transform context stack in the same way
        context1 = program.run()
        context2 = mapped_program.run()
        assert context1.stack == context2.stack
