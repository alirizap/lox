import sys
from pathlib import Path
from plox.errors import LoxRuntimeError
from plox.interpreter import Interpreter
from plox.parser import Parser
from plox.scanner import Scanner
from plox.token import Token
from plox.token_type import TokenType


class Lox:
    def __init__(self) -> None:
        self.interpreter = Interpreter(self)
        self.had_error = False
        self.had_runtime_error = False

    def run_file(self, path: str) -> None:
        source = Path(path).read_text(encoding="utf-8")
        self.run(source)

        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self) -> None:
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            if line == "":
                continue
            self.run(line)
            self.had_error = False

    def run(self, source: str) -> None:
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self)
        expression = parser.parse()

        if self.had_error or expression is None:
            return

        self.interpreter.interpret(expression)

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def error_at_token(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: LoxRuntimeError) -> None:
        print(f"{error.message}\n[line {error.token.line}]", file=sys.stderr)
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True
