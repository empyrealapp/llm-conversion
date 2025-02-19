class StackEmpty(Exception):
    pass


class CommandError(Exception):
    pass


class StackError(Exception):
    pass


class StackTypeError(StackError):
    pass


class StackValueError(StackError):
    pass
