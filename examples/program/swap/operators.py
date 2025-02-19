from random import randint
from typing import Any

from dowse.dsl.exceptions import StackTypeError
from dowse.dsl.stack import StackOp
from dowse.dsl.types import Address, Boolean, Float, Integer, String, TokenAmount, User


class Random(StackOp):
    """Make a random value between two integers.  The top value on the stack must be lower than the second value on the stack."""

    def operation(self, lower_value: Integer, upper_value: Integer) -> Integer:
        [lower_value, upper_value] = sorted(
            [lower_value, upper_value], key=lambda x: x.value
        )
        return Integer(randint(lower_value.value, upper_value.value))


class MakeUser(StackOp):
    """Convert a username to a User"""

    def operation(self, username: String | User) -> User:
        if isinstance(username, User):
            return username
        return User(username.value)


class UserToAddress(StackOp):
    """Convert a User to an Address"""

    def operation(self, user: User) -> Address:
        return Address(user.value)


class MakeTokenAmount(StackOp):
    """Convert a Float and Address to a TokenAmount"""

    def operation(self, amount: Float, address: Address) -> TokenAmount:
        return TokenAmount((amount, address))


class GetTokenAddress(StackOp):
    """Get the Address of a Token"""

    def operation(self, symbol: String) -> Address:
        return Address(symbol.value)


class ConvertEthToWei(StackOp):
    """Convert a Float to an ETH TokenAmount"""

    def operation(self, amount: Float) -> TokenAmount:
        return TokenAmount(
            (amount, Address("0x4200000000000000000000000000000000000006"))
        )


class ConvertToTokenAmount(StackOp):
    """Convert an Amount and Address to a TokenAmount"""

    def operation(self, amount: Float, address: Address) -> TokenAmount:
        return TokenAmount((amount, address))


class TransferFunds(StackOp):
    """Transfer the TokenAmount to the target address, removing the token amount from the stack."""

    def operation(self, amount: TokenAmount, to_address: Address | User) -> None:
        return None


class MaybeTransferFunds(StackOp):
    """
    If the top element on the stack is true, transfers the TokenAmount to the given address and pushes the new
    TokenAmount on the stack.
    Otherwise pushes the original TokenAmount back onto the stack.
    """

    def operation(
        self,
        do_transfer: Boolean,
        amount: TokenAmount,
        to_address: Address | User,
    ) -> TokenAmount:
        """Weird kludge to make this fully polymorphic because the LLM is struggling a bit with this function"""
        args = do_transfer, amount, to_address
        bool_ = None
        amount_ = None
        to_ = None
        for arg in args:
            if arg.title == "boolean":
                bool_ = arg
            elif arg.title == "token_amount":
                amount_ = arg
            elif arg.title == "address":
                to_ = arg
            elif arg.title == "user":
                to_ = arg

        return amount_

    def type_check(self, *args: Any) -> None:
        bool_count = 0
        token_amount_count = 0
        address_count = 0
        user_count = 0
        for arg in args:
            if isinstance(arg, Boolean):
                bool_count += 1
            elif isinstance(arg, TokenAmount):
                token_amount_count += 1
            elif isinstance(arg, Address):
                address_count += 1
            elif isinstance(arg, User):
                user_count += 1
        if (
            bool_count != 1
            or token_amount_count != 1
            or address_count + user_count != 1
        ):
            raise StackTypeError("Invalid arguments")


class ExchangeFunds(StackOp):
    """Convert a TokenAmount to another Address via a swap, buy, sell, exchange, etc."""

    def operation(self, amount: TokenAmount, to_address: Address) -> TokenAmount:
        return TokenAmount((amount.value[0], to_address))


class GetPercentage(StackOp):
    """Convert a TokenAmount to a percentage of the whole.  First arg must be a TokenAmount, second arg must be a Float between 0 and 1.  Pops them both from the stack and returns the percentage."""

    def operation(self, amount: TokenAmount, percentage: Float) -> TokenAmount:
        return TokenAmount(
            (Float(amount.value[0].value * percentage.value), amount.value[1])
        )


SPECIAL_OPERATORS: list = [
    MakeUser,
    UserToAddress,
    MakeTokenAmount,
    GetTokenAddress,
    ConvertEthToWei,
    ConvertToTokenAmount,
    TransferFunds,
    MaybeTransferFunds,
    ExchangeFunds,
    Random,
    GetPercentage,
]
