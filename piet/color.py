from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Color:
    """
    A codel color as defined in piet (i.e. a valid hue, and a valid level of lightness).
    """

    hue: int
    lightness: int

    hue_names = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
    hue_codes = ['#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF']

    def __init__(self, hue: int, lightness: int):
        self.hue = hue % 6
        self.lightness = lightness % 3

    @classmethod
    def from_name(cls, name: str) -> Color:
        """
        Generate :class:`Color` from human-readable color name.
        """

        if name.startswith('light'):
            lightness, hue_name = 0, name[len('light'):]
        elif name.startswith('dark'):
            lightness, hue_name = 2, name[len('dark'):]
        else:
            lightness, hue_name = 1, name

        try:
            hue = cls.hue_names.index(hue_name)
        except ValueError:
            raise ValueError(f'Invalid color name: "{name}"')

        return Color(hue, lightness)

    @property
    def code(self) -> str:
        """
        RGB code of color (`#RRGGBB`).
        """

        hue_code = self.hue_codes[self.hue]

        if self.lightness == 0:
            code = hue_code.replace('00', 'C0')
        elif self.lightness == 1:
            code = hue_code
        elif self.lightness == 2:
            code = hue_code.replace('FF', 'C0')
        else:
            raise NotImplementedError

        return code

    def __str__(self) -> str:
        """
        Human-readable name of color.
        """

        hue_name = self.hue_names[self.hue]
        if self.lightness == 0:
            return f'light{hue_name}'
        elif self.lightness == 1:
            return hue_name
        elif self.lightness == 2:
            return f'dark{hue_name}'
        else:
            raise NotImplementedError
