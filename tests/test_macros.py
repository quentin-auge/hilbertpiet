from mock import MagicMock

from piet.context import Context
from piet.macros import Macro
from piet.ops import Op


class DummyOp(Op):
    def _call(self, context: Context) -> Context:
        context.value += 1
        context.stack.append(context.value)
        return context


def test_call():
    class A(DummyOp): pass

    class B(DummyOp): pass

    class C(DummyOp): pass

    A.__call__ = MagicMock(side_effect=DummyOp().__call__)
    B.__call__ = MagicMock(side_effect=DummyOp().__call__)
    C.__call__ = MagicMock(side_effect=DummyOp().__call__)

    class TestMacro(Macro):
        @property
        def ops(self):
            return [A(), B(), C()]

    macro = TestMacro()
    macro(Context())

    A.__call__.assert_called_with(Context(stack=[], value=0))
    B.__call__.assert_called_with(Context(stack=[1], value=1))
    C.__call__.assert_called_with(Context(stack=[1, 2], value=2))


def test_cost():
    class A(DummyOp):
        @property
        def _cost(self):
            return 2

    class B(DummyOp):
        @property
        def _cost(self):
            return 3

    class C(DummyOp):
        @property
        def _cost(self):
            return 4

    class TestMacro(Macro):
        @property
        def ops(self):
            return [A(), B(), C()]

    macro = TestMacro()
    assert macro._cost == 2 + 3 + 4
