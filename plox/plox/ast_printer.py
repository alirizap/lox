from plox.expr import Expr, ExprVisitor, Binary, Grouping, Literal, Unary


class ASTPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesis(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesis("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesis(expr.operator.lexeme, expr.right)

    def _parenthesis(self, name: str, *exprs: Expr) -> str:
        result = "(" + name

        for expr in exprs:
            result += " "
            result += expr.accept(self)
        result += ")"
        return result
