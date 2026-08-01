from plox.token import Token


class ParseError(RuntimeError):
    pass


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message
