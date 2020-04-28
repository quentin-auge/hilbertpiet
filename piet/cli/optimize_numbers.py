from __future__ import annotations

import argparse
import operator
import pickle
from math import log, sqrt
from pathlib import Path

from piet.numbers import PushNumber


class PushNumberOptimizer:
    def __init__(self, max_num: int):
        self.max_num = max_num
        self.nums = {n: PushNumber(n) for n in range(1, max_num + 1)}

    def _optimize_add(self):
        for i in range(2, self.max_num - 2 + 1):
            for j in range(i, self.max_num - i + 1):
                self._step(operator.add, i, j)

    def _optimize_sub(self):
        for i in range(self.max_num, 1, -1):
            for j in range(1, i):
                self._step(operator.sub, i, j)

    def _optimize_mult(self):
        for i in range(2, self.max_num // 2 + 1):
            for j in range(i, self.max_num // i + 1):
                self._step(operator.mul, i, j)

    def _optimize_div(self):
        for i in range(self.max_num, 1, -1):
            for j in range(2, i // 2):
                self._step(operator.floordiv, i, j)

    def _optimize_pow(self):
        for i in range(2, int(sqrt(self.max_num) + 1)):
            for j in range(2, int(log(self.max_num, i) + 1)):
                self._step(operator.pow, i, j)

    def _step(self, binary_op, i: int, j: int):
        old_cost = self.nums[binary_op(i, j)]._cost

        candidate_ast = binary_op(self.nums[i]._ast, self.nums[j]._ast)
        new_cost = candidate_ast._cost

        if new_cost < old_cost:
            self.nums[binary_op(i, j)]._ast = candidate_ast

    @property
    def _cost(self):
        return sum(num._cost for num in self.nums.values())

    def save(self, out_filepath: Path):
        asts = {n: self.nums[n]._ast for n in self.nums}
        with out_filepath.open('wb') as f:
            pickle.dump(asts, f)


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

        optimizations = [opt._optimize_pow,
                         opt._optimize_mult, opt._optimize_div,
                         opt._optimize_add, opt._optimize_sub] * 2

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
