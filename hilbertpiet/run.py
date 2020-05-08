import logging
from dataclasses import dataclass
from typing import List

from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Init, Op

LOGGER = logging.getLogger(__name__)


@dataclass(eq=False)
class Program(Macro):
    """
    A Piet program, with facilities to run and render program.
    """

    _ops: List[Op]

    def __init__(self, _ops: List[Op], /):
        self._ops = _ops
        self._context = Context()

    @property
    def ops(self):
        return [Init()] + self._ops

    def run(self) -> Context:
        """
        Run program and log result.
        """

        context = Context()

        for op in self.ops:
            if isinstance(op, Macro):
                # Log macro name and execute expanded ops
                LOGGER.debug(str(op))
                for op in op.expanded_ops:
                    context = self.__step(op, context, indent_logging=True)
            else:
                context = self.__step(op, context, indent_logging=False)

        return context

    def __step(self, op, context, indent_logging=False):
        """
        Execute program operation and log result.
        """
        context = op(context)
        indent = '  ' if indent_logging else ''
        LOGGER.debug(f'{indent}{op} {context}')
        return context
