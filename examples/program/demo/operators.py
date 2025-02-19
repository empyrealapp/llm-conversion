from random import randint

from dowse.dsl.operators.stack_op import StackOp
from dowse.dsl.types import Address, Integer


class MakeRandomValue(StackOp):
    """Make a random value between two integers"""

    def operation(self, lower_value: Integer, upper_value: Integer) -> Integer:
        return Integer(randint(lower_value.value, upper_value.value))
