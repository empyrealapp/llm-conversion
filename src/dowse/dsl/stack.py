from typing import Any

from pydantic import BaseModel, Field

from .exceptions import StackEmpty
from .operators.stack_op import StackOp
from .types import Wrapper


class Stack(BaseModel):
    stack: list[Wrapper[Any]] = Field(default_factory=list)
    operators: dict[str, "StackOp"] = Field(default_factory=dict)

    variables: dict[str, Wrapper[Any]] = Field(default_factory=dict)

    def roll(self, n: int) -> None:
        nth_element = self.stack[n]
        self.stack = self.stack[:n] + self.stack[n + 1 :] + [nth_element]

    def assign(self, variable_name: str, value: Wrapper[Any]) -> None:
        self.variables[variable_name] = value

    def push(self, *values: Wrapper[Any]) -> None:
        self.stack.extend(values)

    def pop(self) -> Wrapper[Any]:
        if self.is_empty():
            raise StackEmpty("tried to pop from an empty stack")
        return self.stack.pop()

    def peek(self) -> Wrapper[Any]:
        if self.is_empty():
            raise StackEmpty("tried to peek at an empty stack")
        return self.stack[-1]

    def is_empty(self) -> bool:
        return len(self.stack) == 0

    def execute_line(self, line: str) -> None:
        line = line.split("//")[0].strip()
        if not line:
            return
        line, *args = line.split()
        self.call(line, *args)

    def call(self, command: str, *args: Any) -> None:
        if command == "ROLL":
            stack_arg = self.pop()
            self.roll(stack_arg.value)
            return
        if command == "PUSH" and args and args[0].startswith("&"):
            variable_name = args[0][1:]
            self.push(self.variables[variable_name])
            return
        elif command == "ASSIGN":
            variable_name = args[0]
            stack_arg = self.pop()
            self.assign(variable_name, stack_arg)
            self.push(stack_arg)
            return

        function = self.operators[command]

        if function.immediate_instruction:
            result = function.operation(*args)
        else:
            stack_args = [self.pop() for _ in range(function.arg_count)]
            try:
                function.type_check(*stack_args)
                result = function.operation(*stack_args)
            except Exception as e:
                for arg in stack_args[::-1]:
                    self.push(arg)
                raise e
        if result is not None:
            if isinstance(result, tuple):
                for result_arg in result[::-1]:
                    self.push(result_arg)
            else:
                self.push(result)

    def register_operators(self, operators: list["StackOp"]) -> None:
        self.operators = {operator.name(): operator for operator in operators}

    def __repr__(self) -> str:
        return f"{self.stack[::-1]}"

    __str__ = __repr__
