from typing import Any, Iterator

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic._internal._model_construction import ModelMetaclass

from dowse.dsl.example import EXAMPLE_PROGRAM
from dowse.dsl.exceptions import StackEmpty, StackError, StackTypeError, StackValueError
from dowse.dsl.operators import BASE_OPERATORS, StackOp
from dowse.dsl.stack import Stack
from dowse.dsl.syntax import make_syntax_doc
from dowse.dsl.types import DEFAULT_TYPES
from dowse.interfaces import Executor


class UserRequest(BaseModel):
    content: str
    username: str


class Command(BaseModel):
    code_block: list[str]

    def print(self) -> None:
        idx = 0
        for line in self.code_block:
            if line.split("//")[0].strip() == "":
                continue
            print(f"{idx}: {line}")
            idx += 1

    def lines(self) -> Iterator[str]:
        for line in self.code_block:
            if line.startswith("//"):
                continue
            yield line


class DowseExecutor(
    Executor[
        UserRequest,  # the input type of the first processor
        UserRequest,  # type once all processors are run
        Command,  # the output type of the last processor
    ]
):
    prompt: str = ""
    types: list[ModelMetaclass] = DEFAULT_TYPES
    base_operators: list[type[StackOp]] = BASE_OPERATORS
    special_operators: list[type[StackOp]] = []
    example_programs: list[str] = [EXAMPLE_PROGRAM]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @computed_field  # type: ignore[misc]
    @property
    def operators(self) -> list[StackOp]:
        return [op() for op in self.base_operators + self.special_operators]

    @computed_field  # type: ignore[misc]
    @property
    def operator_map(self) -> dict[str, StackOp]:
        return {op.name(): op for op in self.operators}

    def model_post_init(self, __context: Any):
        self.prompt = make_syntax_doc(
            self.types,
            "\n---\n".join(self.example_programs),
            special_operators=self.special_operators,
        )
        super().model_post_init(__context)

    def simulate(self, command: Command, verbose: bool = False) -> Stack:
        stack = Stack()
        stack.register_operators(self.operators)

        for idx, line in enumerate(command.lines()):
            try:
                stack.execute_line(line)
            except StackTypeError as e:
                raise StackError(idx, line, e, stack)
            except StackValueError as e:
                raise StackError(idx, line, e, stack)
            except StackEmpty as e:
                raise StackError(idx, line, e, stack)
            if verbose:
                print(line)
                print("Stack: ", stack)
        return stack

    async def solve(
        self,
        query: UserRequest,
        max_errors: int = 10,
        verbose: bool = False,
    ) -> Command:
        error_count = 0
        response = await self.execute(
            query,
            persist_agent=True,
        )
        while error_count < max_errors:
            if response.content is None:
                raise Exception(f"Execution Error: {response.error_message}")

            code = response.content
            if verbose:
                print("CODE BLOCK:")
                code.print()
            try:
                self.simulate(code, verbose=False)
                return code

            except StackError as e:
                (idx, line, error, stack) = e.args
                error_str = f"Error executing line {idx}:{line}: {error}.  Stack currently: {stack}"

                if verbose:
                    print(f"\n\nERROR:{error_str}\n\n")

                response = await self.execute(
                    UserRequest(
                        content=f"{error_str}\nPlease fix program and try again",
                        username="@user1",
                    ),
                    persist_agent=True,
                )
        raise Exception("Max errors reached")
