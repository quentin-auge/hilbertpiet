from __future__ import annotations

import argparse
import logging
import operator
import pickle
from math import log, sqrt
from pathlib import Path

from hilbertpiet.numbers import PushNumber

LOGGER = logging.getLogger(__name__)


class PushNumberOptimizer:
    """
    Find the optimal tree representation of a set of numbers constructed from each others, in
    terms of codels needed to produce the number on top of the context stack.

    Attributes:
        max_num: upper bound of the range of numbers to optimize (lower bound is 0).
        nums: the optimized numbers.
    """

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

        candidate_tree = binary_op(self.nums[i]._tree, self.nums[j]._tree)
        new_cost = candidate_tree._cost

        if new_cost < old_cost:
            self.nums[binary_op(i, j)]._tree = candidate_tree

    @property
    def _cost(self):
        """
        Total cost of the range of numbers.
        """
        return sum(num._cost for num in self.nums.values())

    def save(self, out_filepath: Path):
        """
        Save tree representation of numbers into a file.
        """
        trees = {n: self.nums[n]._tree for n in self.nums}
        with out_filepath.open('wb') as f:
            pickle.dump(trees, f)


def main():
    parser = argparse.ArgumentParser('Optimize and pickle numbers')
    rw_group = parser.add_mutually_exclusive_group()
    rw_group.add_argument('--show-only', action='store_true', help='only load and display numbers')
    parser.add_argument('--limit', type=int, nargs='?', default=128,
                        help='limit number to optimize (default: %(default)s)')
    parser.add_argument('filepath', type=Path, help='pickled numbers filepath')
    parser.add_argument('--verbose', '-v', action='store_true', help='debug mode')
    args = parser.parse_args()

    # Setup logging

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(message)s')

    # Optimize numbers

    if not args.show_only:
        opt = PushNumberOptimizer(max_num=args.limit)

        LOGGER.info(f'Round 0: cost={opt._cost}')

        optimizations = [opt._optimize_pow,
                         opt._optimize_mult, opt._optimize_div,
                         opt._optimize_add, opt._optimize_sub] * 2

        for i, optimize in enumerate(optimizations, 1):
            optimize()
            LOGGER.info(f'Round {i}: cost={opt._cost}, {optimize.__name__}')

        LOGGER.info('')
        LOGGER.info(f'Saving numbers to {args.filepath}')
        opt.save(args.filepath)
        LOGGER.info('')

    # Print numbers

    PushNumber.load_numbers(args.filepath)
    for n in range(1, args.limit + 1):
        num = PushNumber(n)
        LOGGER.info(f'{n} = {num.decomposition}')
        LOGGER.debug(f'{repr(num)}.ops = {num.expanded_ops}')
        LOGGER.debug(f'cost = {num._cost}')
        LOGGER.debug('')


if __name__ == '__main__':
    main()
