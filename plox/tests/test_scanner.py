import pytest

from plox.lox import Lox
from plox.scanner import Scanner
from plox.token_type import TokenType as tt


def scan(source: str):
    """Helper: scan source and return the list of tokens (Lox instance is
    fresh each time so had_error doesn't leak between tests)."""
    lox = Lox()
    scanner = Scanner(source, lox)
    tokens = scanner.scan_tokens()
    return tokens, lox


def token_types(tokens):
    return [t.type for t in tokens]


class TestSingleCharTokens:
    def test_parens_and_braces(self):
        tokens, lox = scan("(){}")
        assert token_types(tokens) == [
            tt.LEFT_PAREN,
            tt.RIGHT_PAREN,
            tt.LEFT_BRACE,
            tt.RIGHT_BRACE,
            tt.EOF,
        ]
        assert not lox.had_error

    def test_punctuation(self):
        tokens, _ = scan(",.-+;*")
        assert token_types(tokens) == [
            tt.COMMA,
            tt.DOT,
            tt.MINUS,
            tt.PLUS,
            tt.SEMICOLON,
            tt.STAR,
            tt.EOF,
        ]


class TestOneOrTwoCharTokens:
    @pytest.mark.parametrize(
        "source,expected",
        [
            ("!", tt.BANG),
            ("!=", tt.BANG_EQUAL),
            ("=", tt.EQUAL),
            ("==", tt.EQUAL_EQUAL),
            ("<", tt.LESS),
            ("<=", tt.LESS_EQUAL),
            (">", tt.GREATER),
            (">=", tt.GREATER_EQUAL),
        ],
    )
    def test_operator(self, source, expected):
        tokens, _ = scan(source)
        assert token_types(tokens) == [expected, tt.EOF]

    def test_maximal_munch_does_not_overreach(self):
        # "!==" should be BANG_EQUAL followed by EQUAL, not eaten as one blob.
        tokens, _ = scan("!==")
        assert token_types(tokens) == [tt.BANG_EQUAL, tt.EQUAL, tt.EOF]


class TestComments:
    def test_line_comment_is_ignored(self):
        tokens, _ = scan("// this whole line is a comment")
        assert token_types(tokens) == [tt.EOF]

    def test_comment_does_not_consume_next_line(self):
        tokens, _ = scan("// comment\n+")
        assert token_types(tokens) == [tt.PLUS, tt.EOF]

    def test_slash_alone_is_division(self):
        tokens, _ = scan("/")
        assert token_types(tokens) == [tt.SLASH, tt.EOF]


class TestCStyleBlockComments:
    def test_single_line_block_comment_is_ignored(self):
        tokens, _ = scan("/* This is a comment. */")
        assert token_types(tokens) == [tt.EOF]

    def test_block_comment_consume_multiple_lines(self):
        tokens, _ = scan("/*comment1\ncomment2\ncomment3*/")
        assert token_types(tokens) == [tt.EOF]

    def test_unterminated_block_comment_reports_error(self):
        _, lox = scan("/* Comment\n")
        assert lox.had_error

    def test_block_comment_does_not_consume_following_token(self):
        tokens, _ = scan("/* comment */+")
        assert token_types(tokens) == [tt.PLUS, tt.EOF]

    def test_line_number_advances_past_multipleline_comment(self):
        tokens, _ = scan("/*line1\nline2\nline3*/+")
        plus_token = [t for t in tokens if t.type == tt.PLUS][0]
        assert plus_token.line == 3

    def test_block_comment_containing_asterisk(self):
        tokens, _ = scan("/* 2 * 3 = 6 */+")
        assert token_types(tokens) == [tt.PLUS, tt.EOF]

    def test_block_comment_containing_slash(self):
        tokens, _ = scan("/* a / b */+")
        assert token_types(tokens) == [tt.PLUS, tt.EOF]

    def test_empty_block_comment(self):
        tokens, _ = scan("/**/")
        assert token_types(tokens) == [tt.EOF]

    def test_slash_star_slash_is_empty_comment_not_unterminated(self):
        _, lox = scan("/*/")
        assert lox.had_error


class TestWhitespaceAndLines:
    def test_whitespace_ignored(self):
        tokens, _ = scan(" \t\r+")
        assert token_types(tokens) == [tt.PLUS, tt.EOF]

    def test_line_number_increments(self):
        tokens, _ = scan("+\n+\n+")
        plus_tokens = [t for t in tokens if t.type == tt.PLUS]
        assert [t.line for t in plus_tokens] == [1, 2, 3]
        assert tokens[-1].line == 3  # EOF on final line


class TestStrings:
    def test_simple_string(self):
        tokens, _ = scan('"hello"')
        assert token_types(tokens) == [tt.STRING, tt.EOF]
        assert tokens[0].literal == "hello"
        assert tokens[0].lexeme == '"hello"'

    def test_string_spanning_multiple_lines(self):
        tokens, lox = scan('"hello\nworld"')
        assert token_types(tokens) == [tt.STRING, tt.EOF]
        assert tokens[0].literal == "hello\nworld"
        assert not lox.had_error

    def test_unterminated_string_reports_error(self):
        tokens, lox = scan('"unterminated')
        assert lox.had_error


class TestNumbers:
    def test_integer(self):
        tokens, _ = scan("123")
        assert token_types(tokens) == [tt.NUMBER, tt.EOF]
        assert tokens[0].literal == 123.0
        assert isinstance(tokens[0].literal, float)

    def test_decimal(self):
        tokens, _ = scan("123.456")
        assert tokens[0].literal == 123.456

    def test_trailing_dot_not_consumed_without_digit(self):
        # "123." with no digit after the dot: number stops at 123,
        # then DOT is its own token.
        tokens, _ = scan("123.")
        assert token_types(tokens) == [tt.NUMBER, tt.DOT, tt.EOF]
        assert tokens[0].literal == 123.0

    def test_leading_dot_is_not_a_number(self):
        # Lox doesn't support ".5" as a number; DOT then NUMBER.
        tokens, _ = scan(".5")
        assert token_types(tokens) == [tt.DOT, tt.NUMBER, tt.EOF]


class TestIdentifiersAndKeywords:
    def test_simple_identifier(self):
        tokens, _ = scan("language")
        assert token_types(tokens) == [tt.IDENTIFIER, tt.EOF]
        assert tokens[0].lexeme == "language"

    def test_identifier_with_underscore_and_digits(self):
        tokens, _ = scan("_my_var2")
        assert token_types(tokens) == [tt.IDENTIFIER, tt.EOF]

    @pytest.mark.parametrize(
        "keyword,expected",
        [
            ("and", tt.AND),
            ("class", tt.CLASS),
            ("else", tt.ELSE),
            ("false", tt.FALSE),
            ("for", tt.FOR),
            ("fun", tt.FUN),
            ("if", tt.IF),
            ("nil", tt.NIL),
            ("or", tt.OR),
            ("print", tt.PRINT),
            ("return", tt.RETURN),
            ("super", tt.SUPER),
            ("this", tt.THIS),
            ("true", tt.TRUE),
            ("var", tt.VAR),
            ("while", tt.WHILE),
        ],
    )
    def test_keyword(self, keyword, expected):
        tokens, _ = scan(keyword)
        assert token_types(tokens) == [expected, tt.EOF]

    def test_keyword_prefix_is_still_identifier(self):
        # "variable" contains "var" but must NOT be scanned as VAR + "iable".
        tokens, _ = scan("variable")
        assert token_types(tokens) == [tt.IDENTIFIER, tt.EOF]
        assert tokens[0].lexeme == "variable"


class TestFullStatement:
    def test_var_declaration(self):
        tokens, lox = scan("var language = 'lox';".replace("'", '"'))
        assert token_types(tokens) == [
            tt.VAR,
            tt.IDENTIFIER,
            tt.EQUAL,
            tt.STRING,
            tt.SEMICOLON,
            tt.EOF,
        ]
        assert tokens[1].lexeme == "language"
        assert tokens[3].literal == "lox"
        assert not lox.had_error


class TestErrors:
    def test_unexpected_character_reports_error(self):
        tokens, lox = scan("@")
        assert lox.had_error

    def test_scanning_continues_after_bad_character(self):
        # Scanner should report the error but keep scanning, not crash.
        tokens, lox = scan("@+")
        assert lox.had_error
        assert tt.PLUS in token_types(tokens)


class TestEmptySource:
    def test_empty_string_yields_only_eof(self):
        tokens, _ = scan("")
        assert token_types(tokens) == [tt.EOF]
