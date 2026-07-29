from typing import Any
from plox.token import Token
from plox.token_type import TokenType as tt


class Scanner:
    def __init__(self, source: str, lox) -> None:
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.lox = lox
        self.keywords = {
            "and": tt.AND,
            "class": tt.CLASS,
            "else": tt.ELSE,
            "false": tt.FALSE,
            "for": tt.FOR,
            "fun": tt.FUN,
            "if": tt.IF,
            "nil": tt.NIL,
            "or": tt.OR,
            "print": tt.PRINT,
            "return": tt.RETURN,
            "super": tt.SUPER,
            "this": tt.THIS,
            "true": tt.TRUE,
            "var": tt.VAR,
            "while": tt.WHILE,
        }

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(tt.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case "(":
                self.add_token(tt.LEFT_PAREN)
            case ")":
                self.add_token(tt.RIGHT_PAREN)
            case "{":
                self.add_token(tt.LEFT_BRACE)
            case "}":
                self.add_token(tt.RIGHT_BRACE)
            case ",":
                self.add_token(tt.COMMA)
            case ".":
                self.add_token(tt.DOT)
            case "-":
                self.add_token(tt.MINUS)
            case "+":
                self.add_token(tt.PLUS)
            case ";":
                self.add_token(tt.SEMICOLON)
            case "*":
                self.add_token(tt.STAR)
            case "!":
                self.add_token(tt.BANG_EQUAL if self.match("=") else tt.BANG)
            case "=":
                self.add_token(tt.EQUAL_EQUAL if self.match("=") else tt.EQUAL)
            case "<":
                self.add_token(tt.LESS_EQUAL if self.match("=") else tt.LESS)
            case ">":
                self.add_token(tt.GREATER_EQUAL if self.match("=") else tt.GREATER)
            case "/" if self.match("/"):
                # A comment goes until the end of the line.
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            case "/" if self.match("*"):
                # C-style /* ... */ block comments.
                while (
                    not (self.peek() == "*" and self.peek_next() == "/")
                    and not self.is_at_end()
                ):
                    if self.peek() == "\n":
                        self.line += 1
                    self.advance()
                if self.is_at_end():
                    self.lox.error(self.line, "Unterminated block comment.")
                    return

                self.advance()
                self.advance()
            case "/":
                self.add_token(tt.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case c if c.isdigit():
                self.number()
            case c if c.isalpha() or c == "_":
                self.identifier()
            case _:
                self.lox.error(self.line, "Unexpected character.")

    def identifier(self) -> None:
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[self.start : self.current]
        type = self.keywords.get(text, tt.IDENTIFIER)
        self.add_token(type)

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start : self.current])
        self.add_token(tt.NUMBER, value)

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.lox.error(self.line, "Unterminated string.")
            return

        # The closing ".
        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(tt.STRING, value)

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, type: tt, literal: Any = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
