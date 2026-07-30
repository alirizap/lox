import pytest

from plox.lox import Lox
from plox.scanner import Scanner
from plox.parser import Parser
from plox.expr import Binary, Grouping, Literal, Unary
from plox.ast_printer import ASTPrinter
from plox.token_type import TokenType as tt


def parse(source: str):
    """Helper: scan + parse source, return (expr, lox) so tests can also
    check error state. Fresh Lox instance each time."""
    lox = Lox()
    tokens = Scanner(source, lox).scan_tokens()
    expr = Parser(tokens, lox).parse()
    return expr, lox


def print_expr(source: str) -> str:
    expr, _ = parse(source)
    assert expr is not None
    return ASTPrinter().print(expr)


class TestPrimary:
    def test_number_literal(self):
        expr, lox = parse("123")
        assert isinstance(expr, Literal)
        assert expr.value == 123.0
        assert not lox.had_error

    def test_string_literal(self):
        expr, _ = parse('"hello"')
        assert isinstance(expr, Literal)
        assert expr.value == "hello"

    def test_true(self):
        expr, _ = parse("true")
        assert isinstance(expr, Literal)
        assert expr.value is True

    def test_false(self):
        expr, _ = parse("false")
        assert isinstance(expr, Literal)
        assert expr.value is False

    def test_nil(self):
        expr, _ = parse("nil")
        assert isinstance(expr, Literal)
        assert expr.value is None

    def test_grouping(self):
        expr, _ = parse("(123)")
        assert isinstance(expr, Grouping)
        assert isinstance(expr.expression, Literal)
        assert expr.expression.value == 123.0

    def test_missing_expression_reports_error(self):
        expr, lox = parse("")
        assert lox.had_error

    def test_unclosed_paren_reports_error(self):
        expr, lox = parse("(1 + 2")
        assert lox.had_error
        assert expr is None


class TestUnary:
    def test_negative_number(self):
        expr, _ = parse("-123")
        assert isinstance(expr, Unary)
        assert expr.operator.type == tt.MINUS
        assert isinstance(expr.right, Literal)
        assert expr.right.value == 123.0

    def test_not(self):
        expr, _ = parse("!true")
        assert isinstance(expr, Unary)
        assert expr.operator.type == tt.BANG

    def test_double_negative_is_right_associative(self):
        # --5 should parse as -(-5), i.e. nested Unary nodes.
        expr, _ = parse("--5")
        assert isinstance(expr, Unary)
        assert isinstance(expr.right, Unary)
        assert isinstance(expr.right.right, Literal)
        assert expr.right.right.value == 5.0


class TestBinaryPrecedence:
    @pytest.mark.parametrize(
        "source,expected",
        [
            ("1 + 2", "(+ 1.0 2.0)"),
            ("1 - 2", "(- 1.0 2.0)"),
            ("1 * 2", "(* 1.0 2.0)"),
            ("1 / 2", "(/ 1.0 2.0)"),
            ("1 == 2", "(== 1.0 2.0)"),
            ("1 != 2", "(!= 1.0 2.0)"),
            ("1 < 2", "(< 1.0 2.0)"),
            ("1 <= 2", "(<= 1.0 2.0)"),
            ("1 > 2", "(> 1.0 2.0)"),
            ("1 >= 2", "(>= 1.0 2.0)"),
        ],
    )
    def test_single_binary_op(self, source, expected):
        assert print_expr(source) == expected

    def test_multiplication_binds_tighter_than_addition(self):
        # 1 + 2 * 3 should parse as 1 + (2 * 3), not (1 + 2) * 3.
        assert print_expr("1 + 2 * 3") == "(+ 1.0 (* 2.0 3.0))"

    def test_comparison_binds_tighter_than_equality(self):
        assert print_expr("1 < 2 == 3 < 4") == "(== (< 1.0 2.0) (< 3.0 4.0))"

    def test_parentheses_override_precedence(self):
        assert print_expr("(1 + 2) * 3") == "(* (group (+ 1.0 2.0)) 3.0)"

    def test_addition_is_left_associative(self):
        # 1 - 2 - 3 should parse as (1 - 2) - 3, not 1 - (2 - 3).
        assert print_expr("1 - 2 - 3") == "(- (- 1.0 2.0) 3.0)"

    def test_factor_is_left_associative(self):
        assert print_expr("8 / 4 / 2") == "(/ (/ 8.0 4.0) 2.0)"


class TestComplexExpressions:
    def test_matches_book_example(self):
        # The canonical example from the ASTPrinter chapter:
        # -123 * (45.67)
        assert print_expr("-123 * (45.67)") == "(* (- 123.0) (group 45.67))"

    def test_nested_grouping(self):
        assert print_expr("((1))") == "(group (group 1.0))"

    def test_mixed_operators_and_grouping(self):
        source = "1 + 2 * (3 - 4) / 5"
        expected = "(+ 1.0 (/ (* 2.0 (group (- 3.0 4.0))) 5.0))"
        assert print_expr(source) == expected


class TestErrorReporting:
    def test_unexpected_token_reports_error(self):
        expr, lox = parse("+")
        assert lox.had_error
        assert expr is None

    def test_missing_closing_paren_message(self, capsys):
        _, lox = parse("(1 + 2")
        assert lox.had_error
        captured = capsys.readouterr()
        assert "Expect ')' after expression." in captured.err

    def test_trailing_garbage_after_valid_expression(self):
        # Book's simple parser only parses ONE expression; leftover tokens
        # like a stray ")" after a valid expr are not itself an error at
        # this stage (no top-level "expect EOF" check yet), so this
        # documents current behavior rather than asserting an error.
        expr, lox = parse("1 + 2)")
        assert isinstance(expr, Binary)
        assert not lox.had_error
