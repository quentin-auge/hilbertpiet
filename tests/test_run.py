from dataclasses import dataclass
from typing import List
from unittest import mock

from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Init, Op
from hilbertpiet.run import Program


@dataclass
class A(Op): pass


@dataclass
class B(Op): pass


@dataclass
class C(Op): pass


class BC(Macro):
    @property
    def ops(self) -> List[Op]:
        return [B(), C()]


@dataclass
class D(Op): pass


def test_program_ops():
    ops = [A(), BC(), D()]
    program_ops = Program(ops).ops
    assert program_ops == [Init()] + ops


def test_program_run():
    context1 = Context(value=1, position=1)
    context2 = Context(position=2 + 2j)
    context3 = Context(position=3 + 3j)
    context4 = Context(position=4 + 4j)
    context5 = Context(stack=[5], value=5, position=5 + 5j, dp=1, output='five')

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
