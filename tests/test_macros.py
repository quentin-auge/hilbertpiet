from mock import MagicMock

from piet.context import Context
from piet.macros import Macro
from piet.ops import Op


def test_call():
    class TestOp(Op):
        def _call(self, context: Context) -> Context:
            context.value += 1
            context.stack.append(context.value)
            return context

    class A(TestOp): pass

    class B(TestOp): pass

    class C(TestOp): pass

    A.__call__ = MagicMock(side_effect=TestOp().__call__)
    B.__call__ = MagicMock(side_effect=TestOp().__call__)
    C.__call__ = MagicMock(side_effect=TestOp().__call__)

    class TestMacro(Macro):
        @property
        def ops(self):
            return [A(), B(), C()]

    macro = TestMacro()
    macro(Context())

    A.__call__.assert_called_with(Context(stack=[], value=0))
    B.__call__.assert_called_with(Context(stack=[1], value=1))
    C.__call__.assert_called_with(Context(stack=[1, 2], value=2))
