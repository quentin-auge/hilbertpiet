from dataclasses import dataclass

from typing import List


@dataclass
class Context:
    """
    A Piet program execution context. To be mutated by operations.

    Attributes:
        stack: program stack after previous codel
        value: size of previous codel, for push operation
        position: position of next codel
        dp: directional pointer; indicated the direction of the next codel
        output: stdout of the program
    """

    stack: List[int]
    value: int
    position: complex
    dp: complex
    output: str

    _DPS_VALUES = [1, 1j, -1, -1j]
    _DPS_STR = ['🡺', '🡻', '🡸', '🡹']

    def __init__(self, stack: List[int] = None, value: int = 0,
                 position: complex = 0j, dp: complex = 1,
                 output: str = ''):
        self.stack = stack or []
        self.value = value
        self.position = position

        if dp not in self._DPS_VALUES:
            raise ValueError(f'Invalid dp value: "{dp}"')

        self.dp = dp
        self.output = output

    def update_position(self, steps: int):
        """
        Move position `steps` times in the direction of dp.
        """
        self.position += steps * self.dp

    def rotate_dp(self, steps: int):
        """
        Rotate directional pointer `steps` times by 90° clockwise.
        """
        self.dp *= 1j ** steps

    def __str__(self):
        dp_str = self._DPS_STR[self._DPS_VALUES.index(self.dp)]
        return f'{self.stack} {self.value} {self.position} {dp_str}'
