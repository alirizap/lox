from typing import Any
from plox.expr import (
    Expr,
    ExprVisitor,
    Assign,
    Binary,
    Grouping,
    Unary,
    Literal,
    Variable,
)
from plox.stmt import Stmt, StmtVisitor, Print, Expression, Var
from plox.token import Token
from plox.token_type import TokenType as tt
from plox.environment import Environment
from plox.errors import LoxRuntimeError


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, lox) -> None:
        self.lox = lox
        self.environment = Environment()

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            self.lox.runtime_error(error)

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case tt.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case tt.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case tt.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case tt.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case tt.BANG_EQUAL:
                return not self.is_equal(left, right)
            case tt.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case tt.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            case tt.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(expr.operator, "Division by zero.")
                return left / right
            case tt.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case tt.PLUS:
                match (right, left):
                    case (float(), float()):
                        return left + right
                    case (str(), str()):
                        return left + right
                    case _:
                        raise LoxRuntimeError(
                            expr.operator, "Operands must be two numbers or two strings"
                        )

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
                self.check_number_operand(expr.operator, right)
                return -float(right)

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.environment.get(expr.name)

    def check_number_operand(self, operator: Token, operand: Any) -> None:
        match operand:
            case float():
                return
            case _:
                raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        match (left, right):
            case (float(), float()):
                return
            case _:
                raise LoxRuntimeError(operator, "Operands must be a number.")

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

    def stringify(self, object: Any) -> str:
        match object:
            case None:
                return "nil"
            case float():
                text = str(object)
                if text.endswith(".0"):
                    text = text[: len(text) - 2]
                return text
            case _:
                return str(object)
