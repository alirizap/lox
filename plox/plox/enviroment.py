from typing import Any
from plox.token import Token
from plox.errors import LoxRuntimeError


class Environment:
    def __init__(self) -> None:
        self.values = dict()

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name in self.values:
            return self.values[name]

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
