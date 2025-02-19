from .base import BASE_OPERATORS
from .special import SPECIAL_OPERATORS
from .stack_op import StackOp

OPERATORS = BASE_OPERATORS + SPECIAL_OPERATORS


__all__ = [
    "BASE_OPERATORS",
    "OPERATORS",
    "SPECIAL_OPERATORS",
    "StackOp",
]
