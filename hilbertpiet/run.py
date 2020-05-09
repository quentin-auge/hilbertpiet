import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

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
