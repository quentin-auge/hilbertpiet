import argparse
import io
import logging
import string
import sys
from pathlib import Path

from hilbertpiet.color import Color
from hilbertpiet.numbers import PushNumber
from hilbertpiet.ops import OutChar
from hilbertpiet.path import NotEnoughSpace, generate_path, map_path_u_turns, map_program_to_path
from hilbertpiet.run import Program

LOGGER = logging.getLogger(__name__)


def main():
    description = 'Generate a Hilbert-curve-shaped Piet program printing a given string'
    parser = argparse.ArgumentParser(description=description)
    input_parser = parser.add_mutually_exclusive_group()
    input_parser.add_argument('--file', '-f', type=argparse.FileType('r'),
                              dest='input', help='input string file (default stdin)')
    input_parser.add_argument('--input', '-i', type=io.StringIO,
                              dest='input', help='input string (default stdin)')
    parser.add_argument('--verbose', '-v', action='store_true', help='debug mode')
    parser.add_argument('--codel-size', '-n', type=int, default=20,
                        help='output codel size (default: %(default)s)')
    parser.add_argument('--initial-color', '-c', type=str, default='red',
                        help='initial color (default: %(default)s)')
    parser.add_argument('--out', '-o', type=Path, required=True, help='output image file')
    parser.set_defaults(input=sys.stdin)
    args = parser.parse_args()

    # Setup logging

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(message)s')

    # Read input

    input = ''.join(args.input.readlines())
    LOGGER.info(f'Input length = {len(input)}')

    num_chars = [ord(c) for c in input if c in set(string.printable)]
    LOGGER.info(f'Skipping {len(input) - len(num_chars)} non-ascii characters')

    LOGGER.info('')

    # Create program

    MODULE_ROOT: Path = Path(__file__).parent.parent
    PushNumber.load_numbers(MODULE_ROOT / 'data' / 'numbers.pkl')

    ops = []
    for num_char in num_chars:
        ops += [PushNumber(num_char), OutChar()]
    program = Program(ops)

    LOGGER.info(f'{program.size} codels before mapping')
    LOGGER.debug(f'Piet operations = {program.ops}')
    LOGGER.info('')

    # Create path and map program

    # Fine-tune necessary number of Hilbert curve iterations within a certain range
    max_iterations = 4
    iterations = 1
    success = False
    while not success:
        path = generate_path(iterations)
        path = map_path_u_turns(path)
        try:
            program = map_program_to_path(program, path)
        except NotEnoughSpace:
            if iterations >= max_iterations:
                raise
            else:
                iterations += 1
        else:
            success = True

    LOGGER.info(f'{iterations} Hilbert curve iterations')
    LOGGER.info(f'{program.size} codels after mapping')
    LOGGER.info('')

    # Run program

    context = program.run()

    # Log program output

    printable_output = context.output.strip()
    if '\n' in printable_output:
        # Indent output lines
        printable_output = '\n   ' + printable_output.replace('\n', '\n   ')
    LOGGER.debug('')

    LOGGER.info(f'Ouput: {printable_output}')
    LOGGER.info('')

    # Draw codels

    LOGGER.info(f'Saving program to {args.out}')

    if args.out.suffix == '.gif':
        imgs = []
        for hue in range(6):
            initial_color = str(Color(lightness=1, hue=hue))
            img = program.render(initial_color=initial_color, codel_size=args.codel_size)
            imgs.append(img)
        imgs[0].save(args.out, append_images=imgs[1:], duration=600, loop=0,
                     save_all=True, optimize=False)

    else:
        img = program.render(initial_color=args.initial_color, codel_size=args.codel_size)
        img.save(args.out)


if __name__ == '__main__':
    main()
