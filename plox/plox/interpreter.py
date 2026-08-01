from typing import Any
from plox.expr import Expr, ExprVisitor, Binary, Grouping, Unary, Literal
from plox.token import Token
from plox.token_type import TokenType as tt


class Interpreter(ExprVisitor):
    def evaluate(self, expr: Expr) -> Any:
        expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case tt.GREATER:
                return left > right
            case tt.GREATER_EQUAL:
                return left >= right
            case tt.LESS:
                return left < right
            case tt.LESS_EQUAL:
                return left <= right
            case tt.BANG_EQUAL:
                return not self.is_equal(left, right)
            case tt.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case tt.MINUS:
                return left - right
            case tt.SLASH:
                return left / right
            case tt.STAR:
                return left * right
            case tt.PLUS:
                match (right, left):
                    case (float(), float()):
                        return left + right
                    case (str(), str()):
                        return left + right

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def visit_unary_expr(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case tt.BANG:
                return not self.is_truthy(right)
            case tt.MINUS:
                return -float(right)

    def is_truthy(self, object: Any) -> bool:
        match object:
            case None:
                return False
            case bool():
                return object
            case _:
                return True

    def is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b
