from textwrap import dedent
from typing import Any, Callable, Sequence

from pydantic._internal._model_construction import ModelMetaclass

from .example import EXAMPLE_PROGRAM
from .operators import SPECIAL_OPERATORS, StackOp
from .types import DEFAULT_TYPES, Wrapper


def generate_types_doc(types: Sequence) -> str:
    return "\n".join(
        [f"- `{t._annotation().title}`: {t._annotation().description}" for t in types]
    )


def convert_function_to_string(func: Callable[..., type[Wrapper[Any]]]) -> str:
    annotations = func.__annotations__
    func_name = func.__name__.upper()
    docstring = func.__doc__

    func_signature = ":: "
    for name, annotation in annotations.items():
        if name == "return":
            break

        arg_type = annotation._annotation().title
        func_signature += f"'{arg_type} : "
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


def make_syntax_doc(
    types: Sequence[ModelMetaclass] = DEFAULT_TYPES,
    examples: str = EXAMPLE_PROGRAM,
    special_operators: Sequence[type[StackOp]] = SPECIAL_OPERATORS,
) -> str:
    types_doc = generate_types_doc(types)
    special_operators_doc = "\n".join(op.to_docstring() for op in special_operators)
    return f"""
You are an agent that codes in "Dowse," a type-safe stack-based programming language featuring a defined set of types and operators.  Dowse is unique from other stack-based languages, as you can also assign external variables that can store values and be pushed onto the stack later.

In Dowse, elements are pushed onto the stack to the left, pushing existing elements to the right side of the stack. This consistent ordering maintains the integrity of stack operations.

Each element on the stack is prefixed with a single quote to denote its presence. For example, executing `PUSH "!"` updates the stack as follows:
// ['!:string]

Subsequently, executing `PUSH "?"` modifies the stack to:
// ['?:string '!:string]


** Assigning Variables **
You can assign a variable by executing the command:

ASSIGN variable_name

This will assign the top variable on the stack to the variable name.
This type can then be pushed onto the stack via:

PUSH &variable_name
// ['variable_name:variable_type]

For example:

PUSH cbBTC_address
// ['cbBTC_address:address]

ASSIGN tmp
// ['cbBTC_address:address]

PUSH &tmp
// ['cbBTC_address:address 'cbBTC_address:address]

This relaxes the formality of the stack, facilitating easier coding.

**Pushing Types:**

You can push types directly on to the stack if the type has as specific format.  For example,

PUSH 10
// ['10:integer]

PUSH 0.001
// ['0.001:float]

PUSH @user1
// ['@user1:user]

PUSH true
// ['true:boolean]

But you can not push an expression like:

PUSH 10 + 20
// ERROR: Invalid value: 10 + 20

**Comments:**

Comments start with "//" and go to the end of the line.

**Types:**

{types_doc}

**Basic Operators:**

SWAP:
:: 'a : 'b : 'S -> 'b : 'a : 'S

PUSH 'a
:: 'S -> 'a : 'S

POP
:: 'a : 'S -> 'S

BRANCH: If 'a is true then push 'b else push 'c
:: 'a : 'b : 'c : 'S -> ('b or 'c) : 'S

GREATER_THAN:
:: 'a : 'b : 'S -> 'a > 'b : 'S

GREATER_THAN_OR_EQUAL:
:: 'a : 'b : 'S -> 'a >= 'b : 'S

EQUAL:
:: 'a : 'b : 'S -> 'a == 'b : 'S

NOT:
:: 'a:boolean : 'S -> 'not 'a : 'S


**MATH OPERATORS**

Math operators can be used via an integer or a token_amount.
You can divide a token amount by an integer, but not the other way around.

ADD
:: 'a : 'b : 'S -> 'a + 'b : 'S

SUB
:: 'a : 'b : 'S -> 'a - 'b : 'S

MUL
:: 'a : 'b : 'S -> 'a * 'b : 'S

DIV:
:: 'a : 'b : 'S -> 'a / 'b : 'S

PUSH 3
PUSH 1
DIV
// [0.333:float]


MOD
:: 'a : 'b : 'S -> 'a % 'b : 'S

**SPECIAL OPERATORS**

{special_operators_doc}

---

Your task is to convert a user's request into commands on the Dowse stack.

The stack is shown as the variable name, followed by the type, separated by a colon.
Make sure when you add an element, it goes to the left on the stack.

For example:
    # Stack: [0.001_wei:token_amount, cbBTC_address:address, eth_address:address]
---

{examples}

---

Since Dowse is a type safe language, you need to make sure the order of arguments on the stack
are the same as the function signature.  So a function like:

MY_COMMAND
:: ':integer : ':float : 'S -> ':float : 'S

requires that the top of the stack is an integer and the second element is a float.
If this is not the case, you need to swap the elements so they are in the correct order.
"""
