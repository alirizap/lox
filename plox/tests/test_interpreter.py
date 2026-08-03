import pytest

from plox.lox import Lox
from plox.scanner import Scanner
from plox.parser import Parser
from plox.interpreter import Interpreter
from plox.errors import LoxRuntimeError
from plox.expr import Binary, Grouping, Literal, Unary
from plox.token import Token
from plox.token_type import TokenType as tt


def make_token(type: tt, lexeme: str = "", line: int = 1) -> Token:
    return Token(type, lexeme, None, line)


def evaluate_source(source: str):
    """Helper: scan + parse + evaluate a single expression, returning
    (value, lox). Fresh Lox/Interpreter each call."""
    lox = Lox()
    tokens = Scanner(source, lox).scan_tokens()
    expr = Parser(tokens, lox).parse()
    assert expr is not None, f"failed to parse: {source!r}"
    interpreter = Interpreter(lox)
    return interpreter.evaluate(expr), lox


class TestLiterals:
    def test_number(self):
        value, _ = evaluate_source("123")
        assert value == 123.0

    def test_string(self):
        value, _ = evaluate_source('"hello"')
        assert value == "hello"

    def test_true(self):
        value, _ = evaluate_source("true")
        assert value is True

    def test_false(self):
        value, _ = evaluate_source("false")
        assert value is False

    def test_nil(self):
        value, _ = evaluate_source("nil")
        assert value is None


class TestGrouping:
    def test_grouping_returns_inner_value(self):
        value, _ = evaluate_source("(123)")
        assert value == 123.0

    def test_nested_grouping(self):
        value, _ = evaluate_source("((42))")
        assert value == 42.0


class TestUnary:
    def test_negative_number(self):
        value, _ = evaluate_source("-5")
        assert value == -5.0

    def test_double_negative(self):
        value, _ = evaluate_source("--5")
        assert value == 5.0

    def test_bang_true_is_false(self):
        value, _ = evaluate_source("!true")
        assert value is False

    def test_bang_false_is_true(self):
        value, _ = evaluate_source("!false")
        assert value is True

    def test_bang_nil_is_true(self):
        # nil is falsy, so !nil is true
        value, _ = evaluate_source("!nil")
        assert value is True

    def test_bang_number_is_false(self):
        # any non-nil, non-false value is truthy
        value, _ = evaluate_source("!123")
        assert value is False

    def test_minus_on_string_is_runtime_error(self):
        interpreter = Interpreter(Lox())
        operator = make_token(tt.MINUS, "-")
        expr = Unary(operator, Literal("not a number"))
        with pytest.raises(LoxRuntimeError) as excinfo:
            interpreter.evaluate(expr)
        assert excinfo.value.message == "Operand must be a number."


class TestArithmetic:
    @pytest.mark.parametrize(
        "source,expected",
        [
            ("1 + 2", 3.0),
            ("5 - 3", 2.0),
            ("4 * 2", 8.0),
            ("10 / 4", 2.5),
            ("1 + 2 * 3", 7.0),
            ("(1 + 2) * 3", 9.0),
        ],
    )
    def test_arithmetic(self, source, expected):
        value, _ = evaluate_source(source)
        assert value == expected

    def test_string_concatenation(self):
        value, _ = evaluate_source('"foo" + "bar"')
        assert value == "foobar"

    def test_number_plus_string_is_runtime_error(self):
        interpreter = Interpreter(Lox())
        operator = make_token(tt.PLUS, "+")
        expr = Binary(Literal(1.0), operator, Literal("two"))
        with pytest.raises(LoxRuntimeError) as excinfo:
            interpreter.evaluate(expr)
        assert "numbers or two strings" in excinfo.value.message

    def test_minus_on_strings_is_runtime_error(self):
        interpreter = Interpreter(Lox())
        operator = make_token(tt.MINUS, "-")
        expr = Binary(Literal("a"), operator, Literal("b"))
        with pytest.raises(LoxRuntimeError):
            interpreter.evaluate(expr)

    def test_division_by_zero_matches_python_float_semantics(self):
        with pytest.raises(LoxRuntimeError) as excinfo:
            evaluate_source("1 / 0")
        assert "Division by zero" in excinfo.value.message


class TestComparison:
    @pytest.mark.parametrize(
        "source,expected",
        [
            ("1 < 2", True),
            ("2 < 1", False),
            ("1 <= 1", True),
            ("2 > 1", True),
            ("1 > 2", False),
            ("2 >= 2", True),
        ],
    )
    def test_comparisons(self, source, expected):
        value, _ = evaluate_source(source)
        assert value is expected

    def test_comparison_on_strings_is_runtime_error(self):
        interpreter = Interpreter(Lox())
        operator = make_token(tt.LESS, "<")
        expr = Binary(Literal("a"), operator, Literal("b"))
        with pytest.raises(LoxRuntimeError):
            interpreter.evaluate(expr)


class TestEquality:
    @pytest.mark.parametrize(
        "source,expected",
        [
            ("1 == 1", True),
            ("1 == 2", False),
            ("1 != 2", True),
            ('"a" == "a"', True),
            ('"a" == "b"', False),
            ("nil == nil", True),
            ("true == true", True),
            ("true == false", False),
        ],
    )
    def test_equality(self, source, expected):
        value, _ = evaluate_source(source)
        assert value is expected

    def test_different_types_are_not_equal(self):
        value, _ = evaluate_source('1 == "1"')
        assert value is False

    def test_nil_not_equal_to_number(self):
        value, _ = evaluate_source("nil == 0")
        assert value is False


class TestStringify:
    def test_integer_valued_float_drops_decimal(self):
        interpreter = Interpreter(Lox())
        assert interpreter.stringify(4.0) == "4"

    def test_non_integer_float_keeps_decimal(self):
        interpreter = Interpreter(Lox())
        assert interpreter.stringify(4.5) == "4.5"

    def test_nil_stringifies_to_nil(self):
        interpreter = Interpreter(Lox())
        assert interpreter.stringify(None) == "nil"

    def test_string_stringifies_as_is(self):
        interpreter = Interpreter(Lox())
        assert interpreter.stringify("hello") == "hello"

    def test_bool_stringifies_python_style(self):
        # Note: Python's str(True) == "True", but Lox source spells it
        # lowercase "true". This documents current behavior; the book's
        # Java version has the same mismatch unless explicitly handled.
        interpreter = Interpreter(Lox())
        assert interpreter.stringify(True) == "True"


class TestInterpretIntegration:
    def test_interpret_prints_result(self, capsys):
        lox = Lox()
        tokens = Scanner("1 + 2", lox).scan_tokens()
        expr = Parser(tokens, lox).parse()
        Interpreter(lox).interpret(expr)
        captured = capsys.readouterr()
        assert captured.out.strip() == "3"

    def test_interpret_reports_runtime_error(self, capsys):
        lox = Lox()
        tokens = Scanner('1 + "two"', lox).scan_tokens()
        expr = Parser(tokens, lox).parse()
        Interpreter(lox).interpret(expr)
        assert lox.had_runtime_error
        captured = capsys.readouterr()
        assert "Operands must be two numbers or two strings" in captured.err
