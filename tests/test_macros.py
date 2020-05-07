from mock import MagicMock, PropertyMock

from hilbertpiet.context import Context
from hilbertpiet.macros import Macro
from hilbertpiet.ops import Op


class DummyOp(Op):
    def _call(self, context: Context) -> Context:
        context.value += 1
        context.stack.append(context.value)
        return context


class DummyMacro(Macro):
    @property
    def ops(self):
        return []


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

    A.__call__.assert_called()
    B.__call__.assert_called()
    C.__call__.assert_called()


def test_expand_ops():
    class A(DummyMacro): pass

    class B(DummyOp): pass

    class C(DummyMacro): pass

    expanded_ops_A = PropertyMock()
    A.expanded_ops = expanded_ops_A

    expanded_ops_B = PropertyMock()
    B.expanded_ops = expanded_ops_B

    expanded_ops_C = PropertyMock()
    C.expanded_ops = expanded_ops_C

    class TestMacro(Macro):
        @property
        def ops(self):
            return [A(), B(), C()]

    macro = TestMacro()
    print(macro.expanded_ops)

    assert expanded_ops_A.called
    assert not expanded_ops_B.called
    assert expanded_ops_C.called


def test_size():
    class A(DummyOp):
        @property
        def size(self):
            return 2

    class B(DummyOp):
        @property
        def size(self):
            return 3

    class C(DummyOp):
        @property
        def size(self):
            return 4

    class TestMacro(Macro):
        @property
        def ops(self):
            return [A(), B(), C()]

    macro = TestMacro()
    assert macro.size == 2 + 3 + 4
