from dataclasses import dataclass

from typing import List


@dataclass()
class Context:
    stack: List[int]
    value: int
    dp: int

    def __init__(self, stack: List[int] = None, value: int = 0, dp: int = 0):
        self.stack = stack or []
        self.value = value
        self.dp = dp

    def __str__(self):
        dp_str = ['🡺', '🡻', '🡸', '🡹'][self.dp % 4]
        return f'{self.stack} {self.value} {dp_str}'

    def __deepcopy__(self, _):
        copy = Context(stack=list(self.stack), value=self.value, dp=self.dp)
        return copy
