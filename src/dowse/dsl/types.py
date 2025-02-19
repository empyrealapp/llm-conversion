from typing import Annotated, Generic, TypeVar, get_args

from pydantic import BaseModel, Field

T = TypeVar("T")


class Wrapper(BaseModel, Generic[T]):
    value: T

    def __init__(self, value: T):
        super().__init__(value=value)

    def __repr__(self) -> str:
        return f"'{self.value}:{self.title}"

    __str__ = __repr__

    @classmethod
    def _annotation(cls):
        return get_args(cls.__pydantic_generic_metadata__["args"][0])[1]

    @property
    def title(self):
        return self._annotation().title

    @property
    def description(self):
        return self._annotation().description

    @classmethod
    def name(cls):
        try:
            return cls._annotation().title
        except Exception:
            return str(cls.__pydantic_generic_metadata__["args"][0]).split(".")[-1]


String = Wrapper[Annotated[str, Field(title="string", description="A string")]]
User = Wrapper[
    Annotated[
        str,
        Field(
            title="user",
            description="A user.  Denoted by @username with no quotes, spaces or special characters.",
        ),
    ]
]
Integer = Wrapper[Annotated[int, Field(title="integer", description="An integer")]]
Float = Wrapper[Annotated[float, Field(title="float", description="A float")]]
Boolean = Wrapper[Annotated[bool, Field(title="boolean", description="A boolean")]]
Address = Wrapper[
    Annotated[str, Field(title="address", description="An Ethereum address")]
]
TokenAmount = Wrapper[
    Annotated[
        tuple[Float, Address | User],
        Field(title="token_amount", description="A token amount"),
    ]
]
TokenAmount.__repr__ = lambda self: f"'{self.value[0].value}:{self.title}"  # type: ignore


DEFAULT_TYPES = [
    Address,
    TokenAmount,
    String,
    Integer,
    Float,
    Boolean,
]
