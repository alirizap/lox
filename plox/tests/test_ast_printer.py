from plox.token import Token
from plox.token_type import TokenType
from plox.expr import Binary, Grouping, Literal, Unary
from plox.ast_printer import ASTPrinter


class TestASTPrinter:
    def test_ast_printer(self):
        expression = Binary(
            Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
            Token(TokenType.STAR, "*", None, 1),
            Grouping(Literal(45.67)),
        )
        printer = ASTPrinter()
        assert printer.print(expression) == "(* (- 123) (group 45.67))"
