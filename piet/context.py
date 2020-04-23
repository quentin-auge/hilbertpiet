from typing import List


class Context:
    def __init__(self, stack: List[int] = None, value: int = 0):
        self.stack = stack or []
        self.value = value

    def __repr__(self):
        cls = self.__class__.__name__
        kwargs = [f'stack = {self.stack}']

        if self.value:
            kwargs.append(f'value = {self.value}')

        return f"{cls}({', '.join(kwargs)})"

    def __str__(self):
        result = str(self.stack)

        if self.value:
            result += f'  {self.value}'

        return result

    def __eq__(self, other):
        same_stack = self.stack == other.stack
        same_value = self.value == other.value
        return same_stack and same_value

    def __deepcopy__(self, _):
        copy = Context(stack=list(self.stack), value=self.value)
        return copy
