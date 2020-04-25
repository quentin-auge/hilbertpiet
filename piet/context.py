from dataclasses import dataclass
from typing import List


@dataclass()
class Context:
    stack: List[int]
    value: int

    def __init__(self, stack: List[int] = None, value: int = 0):
        self.stack = stack or []
        self.value = value

    def __str__(self):
        return f'{self.stack} {self.value}'

    def __deepcopy__(self, _):
        copy = Context(stack=list(self.stack), value=self.value)
        return copy
