import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw

from hilbertpiet.color import Color
from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Init, Op

LOGGER = logging.getLogger(__name__)

# (x, y) position
Position = Tuple[int, int]

# (lightness_change, hue_change) color change
Colorchange = Tuple[int, int]


@dataclass(eq=False)
class Program(Macro):
    """
    A Piet program, with facilities to run and render program.
    """

    _ops: List[Op]

    def __init__(self, _ops: List[Op], /):
        self._ops = _ops
        # Cummuative codels color change (in lightness and hue) from first codel of the program
        self.codels: Dict[Position, Colorchange] = {}

    @property
    def ops(self):
        return [Init()] + self._ops

    def run(self) -> Context:
        """
        Run program and log result.
        """

        context = Context()
        self.codels = {}
        previous_color_change = 0 + 0j

        for op in self.ops:

            # Handle macro expansion
            ops = [op]
            indent = 0
            if isinstance(op, Macro):
                LOGGER.debug(str(op))
                indent = 2
                ops = op.expanded_ops

            for op in ops:
                # Update codels

                x, y = (int(context.position.real),
                        int(context.position.imag))

                cum_color_change = previous_color_change + op.color_change
                lightness_change, hue_change = (int(cum_color_change.real),
                                                int(cum_color_change.imag))
                previous_color_change = cum_color_change

                self.codels[(x, y)] = (lightness_change, hue_change)

                # Execute operation
                context = op(context)

                # Log operation execution
                LOGGER.debug(f"{' ' * indent}{op} {context}")

        return context

    def render(self, initial_color: str, codel_size: int) -> Image:
        """
        Render Piet codels.
        """

        # Make sure program was run
        if not self.codels:
            raise RuntimeError("Can't render program; run it first")

        # Image size

        last_x, last_y = max(self.codels.keys())
        # Because codels indices start at 0
        img_size = (last_x + 1, last_y + 1)
        # For additional termination codels
        img_size = (img_size[0] + 1, img_size[1] + 1)
        # Take codel size into account
        img_size = (img_size[0] * codel_size, img_size[1] * codel_size)

        # Create image

        img = Image.new('RGB', img_size, color='white')

        # Render codels

        initial_color = Color.from_name(initial_color)

        for (x, y), (lightness_change, hue_change) in self.codels.items():
            color = Color(initial_color.lightness + lightness_change,
                          initial_color.hue + hue_change)

            self.__render_codel(img, x, y, codel_size, color.code)

        # Render termination codels

        self.__render_termination_codels(img, last_x, last_y, codel_size, initial_color)

        return img

    def __render_termination_codels(self, img: Image, last_x: int, last_y: int, codel_size: int,
                                    initial_color: Color):
        """
        Render termination codels.
        """

        # Perform a last push

        last_lightness_change, last_hue_change = self.codels[(last_x, last_y)]
        termination_color = Color(initial_color.lightness + last_lightness_change + 1,
                                  initial_color.hue + last_hue_change)
        self.__render_codel(img, last_x + 1, last_y, codel_size, termination_color.code)
        self.__render_codel(img, last_x + 1, last_y - 1, codel_size, termination_color.code)
        self.__render_codel(img, last_x + 1, last_y + 1, codel_size, termination_color.code)

        # Add required black codels

        black_color_code = '#000000'
        self.__render_codel(img, last_x, last_y - 1, codel_size, black_color_code)
        self.__render_codel(img, last_x, last_y + 1, codel_size, black_color_code)
        self.__render_codel(img, last_x + 1, last_y - 2, codel_size, black_color_code)

    @staticmethod
    def __render_codel(img: Image, x: int, y: int, codel_size: int, color_code: str):
        """
        Render a given codel.
        """

        draw = ImageDraw.Draw(img)

        # Codel bounding box
        corner1 = (x * codel_size, y * codel_size)
        corner2 = (corner1[0] + codel_size - 1, corner1[1] + codel_size - 1)
        codel_bounding_box = (corner1, corner2)

        # Draw codel
        draw.rectangle(codel_bounding_box, color_code)
