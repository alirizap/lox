import sys
from pathlib import Path
from plox.scanner import Scanner


class Lox:

    def __init__(self) -> None:
        self.had_error = False

    def run_file(self, path: str) -> None:
        source = Path(path).read_text(encoding="utf-8")
        self.run(source)

        if self.had_error:
            sys.exit(65)

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

        for token in tokens:
            print(token)

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str) -> None:
        print(f'[line {line}] Error{where}: {message}', file=sys.stderr)
        self.had_error = True
