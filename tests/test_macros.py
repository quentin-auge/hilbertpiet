from dataclasses import dataclass
from typing import List

import mock

from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Op


class DummyOp(Op):
    def _call(self, context: Context) -> Context:
        return context


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


class ABC(Macro):
    @property
    def ops(self) -> List[Op]:
        return [A(), BC()]


class CABCB(Macro):
    @property
    def ops(self) -> List[Op]:
        return [C(), ABC(), B()]


def test_call():
    context1 = Context(stack=[1], value=1, position=1 + 1j, dp=1, output='one')
    context2 = Context(stack=[2], value=2, position=2 + 2j, dp=1j, output='two')
    context3 = Context(stack=[3], value=3, position=3 + 3j, dp=-1, output='three')
    context4 = Context(stack=[4], value=4, position=4 + 4j, dp=-1j, output='four')

    with mock.patch.object(A, '__call__', return_value=context2) as mock_call_A:
        with mock.patch.object(B, '__call__', return_value=context3) as mock_call_B:
            with mock.patch.object(C, '__call__', return_value=context4) as mock_call_C:
                macro = ABC()
                final_context = macro(context1)

                mock_call_A.assert_called_once_with(context1)
                mock_call_B.assert_called_once_with(context2)
                mock_call_C.assert_called_once_with(context3)

                assert final_context == context4


def test_expanded_ops():
    assert CABCB().expanded_ops == [C(), A(), B(), C(), B()]


def test_size():
    assert CABCB().size == 5
