from enum import IntEnum


class CommandType(IntEnum):
    OKATADUKE = 1,
    WHERE = 2


class Command:
    type = -1
    operands = []

    def __init__(self, _type, _operands):
        self.type = CommandType(int(_type))
        self.operands = _operands

