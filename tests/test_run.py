from dataclasses import dataclass
from typing import List
from unittest import mock

from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Init, Op
from hilbertpiet.run import Program


@dataclass
class A(Op):
    @property
    def color_change(self) -> complex:
        return 1 + 2j


@dataclass
class B(Op):
    @property
    def color_change(self) -> complex:
        return 3 + 4j


@dataclass
class C(Op):
    @property
    def color_change(self) -> complex:
        return 5 + 6j


class BC(Macro):
    @property
    def ops(self) -> List[Op]:
        return [B(), C()]


@dataclass
class D(Op):
    @property
    def color_change(self) -> complex:
        return 7 + 8j


def test_program_ops():
    ops = [A(), BC(), D()]
    program_ops = Program(ops).ops
    assert program_ops == [Init()] + ops


def test_program_run():
    context1 = Context(value=1, position=1)
    context2 = Context(position=1 + 2j)
    context3 = Context(position=3 + 4j)
    context4 = Context(position=5 + 6j)
    context5 = Context(stack=[5], value=5, position=7 + 8j, dp=-1j, output='five')

    with mock.patch.object(A, '__call__', return_value=context2) as mock_call_A:
        with mock.patch.object(B, '__call__', return_value=context3) as mock_call_B:
            with mock.patch.object(C, '__call__', return_value=context4) as mock_call_C:
                with mock.patch.object(D, '__call__', return_value=context5) as mock_call_D:
                    program = Program([A(), BC(), D()])

                    final_context = program.run()

                    mock_call_A.assert_called_once_with(context1)
                    mock_call_B.assert_called_once_with(context2)
                    mock_call_C.assert_called_once_with(context3)
                    mock_call_D.assert_called_once_with(context4)

                    assert final_context == context5

                    assert program.codels == {
                        # Init()
                        (0, 0): (0, 0),
                        # A()
                        (1, 0): (1, 2),
                        # B()
                        (1, 2): (1 + 3, 2 + 4),
                        # C()
                        (3, 4): (1 + 3 + 5, 2 + 4 + 6),
                        # D()
                        (5, 6): (1 + 3 + 5 + 7, 2 + 4 + 6 + 8)
                    }
