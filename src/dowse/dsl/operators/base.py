from typing import Any, ClassVar

from ..exceptions import StackTypeError, StackValueError
from ..types import Boolean, Float, Integer, String, TokenAmount, User, Wrapper
from .stack_op import StackOp


class Swap(StackOp):
    def operation(
        self, arg1: Wrapper[Any], arg2: Wrapper[Any]
    ) -> tuple[Wrapper[Any], Wrapper[Any]]:
        return arg2, arg1

    def type_check(self, *args: Any) -> None:
        pass


class Dup(StackOp):
    def operation(self, arg: Wrapper[Any]) -> tuple[Wrapper[Any], Wrapper[Any]]:
        return arg, arg

    def type_check(self, *args: Any) -> None:
        pass


class GreaterThan(StackOp):
    def operation(self, arg1: Integer, arg2: Integer) -> Boolean:
        return Boolean(arg1.value > arg2.value)


class GreaterThanOrEqual(StackOp):
    def operation(self, arg1: Integer, arg2: Integer) -> Boolean:
        return Boolean(arg1.value >= arg2.value)


class Equal(StackOp):
    def operation(self, arg1: Integer, arg2: Integer) -> Boolean:
        return Boolean(arg1.value == arg2.value)


class Not(StackOp):
    def operation(self, arg: Boolean) -> Boolean:
        return Boolean(not arg.value)


class Push(StackOp):
    immediate_instruction: ClassVar[bool] = True

    def operation(self, arg: str) -> Wrapper[Any]:
        if arg.startswith('"') and arg.endswith('"'):
            return String(arg[1:-1])
        elif arg.startswith("@"):
            return User(arg)
        elif "." in arg and arg.replace(".", "").isdigit():
            return Float(float(arg))
        elif arg.isdigit():
            return Integer(int(arg))
        elif arg in ["true", "false"]:
            return Boolean(arg == "true")
        else:
            raise ValueError(f"Invalid value: {arg}")


class Pop(StackOp):
    def operation(self, arg: Wrapper[Any]) -> None:
        return None

    def type_check(self, *args: Any) -> None:
        pass


class Add(StackOp):
    def operation(
        self,
        a: Integer | Float | TokenAmount,
        b: Integer | Float | TokenAmount,
    ) -> Integer | Float | TokenAmount:
        if a.title == "token_amount" and b.title == "token_amount":
            if a.value[1].value == b.value[1].value:
                a.value[0].value += b.value[0].value  # type: ignore
                return a
            else:
                raise StackValueError(
                    f"Cannot add token amounts from different addresses.  {a.value[1].value} != {b.value[1].value}"
                )
        elif a.title == "token_amount":
            a.value[0].value += b.value  # type: ignore
        else:
            a.value += b.value  # type: ignore
        return a


class Sub(StackOp):
    def operation(
        self,
        a: Integer | Float | TokenAmount,
        b: Integer | Float | TokenAmount,
    ) -> Integer | Float | TokenAmount:
        if a.title == "token_amount":
            if b.title == "token_amount":
                if not a.value[1].value == b.value[1].value:
                    raise StackValueError(
                        "Cannot subtract token amounts from different addresses"
                    )
                a.value[0].value -= b.value[0].value  # type: ignore
            else:
                a.value[0].value -= b.value  # type: ignore
        else:
            a.value -= b.value  # type: ignore
        return a


class Mul(StackOp):
    def operation(
        self,
        a: Integer | Float | TokenAmount,
        b: Integer | Float | TokenAmount,
    ) -> Integer | Float | TokenAmount:
        if a.title == "token_amount" and b.title == "token_amount":
            if a.value[1].value == b.value[1].value:
                a.value[0].value *= b.value[0].value  # type: ignore
                return a
            else:
                raise StackValueError(
                    "Cannot multiply token amounts from different addresses"
                )
        elif a.title == "token_amount":
            a.value[0].value *= b.value  # type: ignore
        else:
            a.value *= b.value  # type: ignore
        return a


class Div(StackOp):
    def operation(
        self,
        a: Integer | Float | TokenAmount,
        b: Integer | Float | TokenAmount,
    ) -> Integer | Float | TokenAmount:
        if b.title == "token_amount":
            raise StackValueError(
                "The second value on the stack can not be a token amount"
            )
        elif a.title == "token_amount":
            a.value[0].value /= b.value  # type: ignore

        return Float(a.value / b.value)


class Mod(StackOp):
    def operation(
        self,
        a: Integer,
        b: Integer,
    ) -> Integer:
        a.value %= b.value  # type: ignore
        return a


class Branch(StackOp):
    def operation(
        self, condition: Boolean, true_value: Wrapper[Any], false_value: Wrapper[Any]
    ) -> Wrapper[Any]:
        if condition.value:
            return true_value
        else:
            return false_value

    def type_check(self, *args: Any):
        if not isinstance(args[0], Boolean):
            raise StackTypeError("The first value on the stack must be a boolean")


BASE_OPERATORS: list[type[StackOp]] = [
    Swap,
    Push,
    Pop,
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    # Dup,
    Branch,
    GreaterThan,
    GreaterThanOrEqual,
    Equal,
    Not,
]
