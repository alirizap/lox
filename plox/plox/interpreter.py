from typing import Any
from plox.expr import Expr, ExprVisitor, Binary, Grouping, Unary, Literal
from plox.token import Token
from plox.token_type import TokenType as tt


class Interpreter(ExprVisitor):
    def evaluate(self, expr: Expr) -> Any:
        expr.accept(self)

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
