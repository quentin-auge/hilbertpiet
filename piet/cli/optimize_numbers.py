from pathlib import Path

from piet.numbers import PushNumber, PushNumberOptimizer


def main():
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    numbers_filepath = PROJECT_ROOT / 'data' / 'numbers.pkl'

    opt = PushNumberOptimizer(max_num=128)

    print(f'Round 0: cost={opt._cost}')

    optimizations = [opt._optimize_pow, opt._optimize_mult, opt._optimize_add] * 2
    for i, optimize in enumerate(optimizations, 1):
        optimize()
        print(f'Round {i}: cost={opt._cost}, {optimize.__name__}')

    print()
    print(f'Saving numbers to {numbers_filepath}')
    opt.save(numbers_filepath)

    print()
    PushNumber.load_numbers(numbers_filepath)
    for n in range(1, opt.max_num + 2):
        num = PushNumber(n)
        print(f'{n} = {num.decomposition:28} cost={num._cost}')


if __name__ == '__main__':
    main()
