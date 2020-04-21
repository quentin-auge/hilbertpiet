from typing import List


class Context:
    def __init__(self, stack: List[int] = None, buffer: int = 0):
        self.stack = stack or []
        self.buffer = buffer

    def __repr__(self):
        cls = self.__class__.__name__
        kwargs = [f'stack = {self.stack}']

        if self.buffer:
            kwargs.append(f'buffer = {self.buffer}')

        return f"{cls}({', '.join(kwargs)})"

    def __str__(self):
        result = str(self.stack)

        if self.buffer:
            result += f'  {self.buffer}'

        return result

    def __eq__(self, other):
        same_stack = self.stack == other.stack
        same_buffer = self.buffer == other.buffer
        return same_stack and same_buffer

    def __deepcopy__(self, _):
        copy = Context(stack=list(self.stack), buffer=self.buffer)
        return copy
