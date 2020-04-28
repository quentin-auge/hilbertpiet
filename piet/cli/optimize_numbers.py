import argparse
from pathlib import Path

from piet.numbers import PushNumber, PushNumberOptimizer


def main():
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DEFAULT_NUMBERS_FILEPATH = PROJECT_ROOT / 'data' / 'numbers.pkl'

    parser = argparse.ArgumentParser('Optimize piet numbers and pickle them')
    parser.add_argument('--out', type=Path, required=False, default=DEFAULT_NUMBERS_FILEPATH,
                        help='path to pickle the result to (default: %(default)s)')
    parser.add_argument('--show-only', action='store_true',
                        help="open output file and read results, don't optimize neither write")
    parser.add_argument('max_num', type=int, nargs='?', default=128,
                        help='largest number to optimize (default: %(default)s)')
    args = parser.parse_args()

    if not args.show_only:
        opt = PushNumberOptimizer(max_num=args.max_num)

        print(f'Round 0: cost={opt._cost}')

        optimizations = [opt._optimize_pow, opt._optimize_mult, opt._optimize_add] * 2
        for i, optimize in enumerate(optimizations, 1):
            optimize()
            print(f'Round {i}: cost={opt._cost}, {optimize.__name__}')

        print()
        print(f'Saving numbers to {args.out}')
        opt.save(args.out)
        print()

    PushNumber.load_numbers(args.out)
    for n in range(1, args.max_num + 1):
        num = PushNumber(n)
        print(f'{n} = {num.decomposition:38} cost={num._cost}')


if __name__ == '__main__':
    main()
