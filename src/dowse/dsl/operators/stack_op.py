import inspect
from abc import ABC
from textwrap import dedent
from types import UnionType
from typing import Any, ClassVar, get_args, get_origin

from pydantic import BaseModel

from dowse.dsl.exceptions import StackTypeError

from ..types import Wrapper


class StackOp(ABC, BaseModel):
    immediate_instruction: ClassVar[bool] = (
        False  # Operations that can take args like 'PUSH'
    )

    def type_check(self, *args: Any) -> None:
        signature = self.signature()
        for index, (arg, arg_type) in enumerate(zip(args, self.arg_types)):
            if not isinstance(arg, arg_type):

                raise StackTypeError(
                    f"Argument {index} to {signature} is of type {arg.title}"
                )

    def operation(self, *args: Any) -> Wrapper[Any] | tuple[Wrapper[Any], ...] | None:
        return None

    @property
    def arg_count(self) -> int:
        return len(inspect.signature(self.operation).parameters)

    @property
    def arg_types(self):
        return [
            arg.annotation
            for arg in inspect.signature(self.operation).parameters.values()
        ]

    def signature(self):
        signature = f"{self.name()} "
        for arg in self.arg_types:
            if get_origin(arg) is UnionType:
                union = "("
                for type_ in get_args(arg):
                    union += f"{type_.name()} | "
                union = union.strip(" | ")
                signature += f"{union}) "
            else:
                signature += f"{arg.name()} "
        signature = signature.strip()
        return signature

    @classmethod
    def name(cls) -> str:
        name = cls.__name__
        return (
            "".join(["_" + i.lower() if i.isupper() else i for i in name])
            .upper()
            .lstrip("_")
        )

    def __repr__(self) -> str:
        return f"{self.name()}"

    __str__ = __repr__

    @classmethod
    def to_docstring(cls) -> str:
        func_signature = ":: "
        annotations = cls.operation.__annotations__
        func_name = cls.name()
        docstring = cls.__doc__
        for name, annotation in annotations.items():
            if name == "return":
                break

            if get_origin(annotation) is UnionType:
                union = "("
                for type_ in get_args(annotation):
                    union += f"{type_.name()} | "
                union = union.strip(" | ")
                func_signature += f"{union}) "
            else:
                func_signature += f"':{annotation._annotation().title} : "
        func_signature += "'S -> "
        return_type = annotations["return"]

        if return_type is None:
            func_signature += "'S"
        else:
            func_signature += f"'{return_type._annotation().title} : 'S"
        return (
            dedent(
                f"""
            {func_name}: {docstring}
            {func_signature}
        """
            ).strip()
            + "\n"
        )
