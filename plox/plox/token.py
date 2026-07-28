from dataclasses import dataclass
from typing import Any
from plox.token_type import TokenType


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        return f'{self.type.name} {self.lexeme} {self.literal}'

