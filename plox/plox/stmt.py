"""
Stmt AST node definations.
GENERATED CODE - produced by tool/generate_ast.py. do not edit by hand.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from plox.token import Token


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any:
        raise NotImplementedError


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_print_stmt(self)


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_var_stmt(self)

