from plox.expr import Expr, Assign, Binary, Grouping, Literal, Unary, Variable
from plox.stmt import Stmt, Print, Var, Expression
from plox.token import Token
from plox.token_type import TokenType as tt
from plox.errors import ParseError


class Parser:
    def __init__(self, tokens: list[Token], lox) -> None:
        self.tokens = tokens
        self.current = 0
        self.lox = lox

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def expression(self) -> Expr:
        return self.assignment()

    def declaration(self) -> Stmt | None:
        try:
            if self.match(tt.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def statement(self) -> Stmt:
        if self.match(tt.PRINT):
            return self.print_statement()

        return self.expression_statement()

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def var_declaration(self) -> Stmt | None:
        name = self.consume(tt.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(tt.EQUAL):
            initializer = self.expression()

        self.consume(tt.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def assignment(self) -> Expr:
        expr = self.equality()

        if self.match(tt.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "invalid assignment target.")

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(tt.GREATER, tt.GREATER_EQUAL, tt.LESS, tt.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(tt.MINUS, tt.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(tt.SLASH, tt.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(tt.BANG, tt.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        if self.match(tt.FALSE):
            return Literal(False)
        if self.match(tt.TRUE):
            return Literal(True)
        if self.match(tt.NIL):
            return Literal(None)
        if self.match(tt.NUMBER, tt.STRING):
            return Literal(self.previous().literal)
        if self.match(tt.IDENTIFIER):
            return Variable(self.previous())
        if self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types: tt) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: tt, message: str) -> Token:
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def check(self, type: tt) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == tt.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str) -> ParseError:
        self.lox.error_at_token(token, message)
        return ParseError()

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().type == tt.SEMICOLON:
                return

            if self.peek().type in (
                tt.CLASS,
                tt.FUN,
                tt.VAR,
                tt.FOR,
                tt.IF,
                tt.WHILE,
                tt.PRINT,
                tt.RETURN,
            ):
                return

            self.advance()
