import sys
from pathlib import Path


def define_ast(output_dir: str, base_name: str, types: list[str]) -> None:
    path = Path(output_dir) / f"{base_name.lower()}.py"

    lines = []
    lines.append('"""')
    lines.append(f"{base_name} AST node definations.")
    lines.append(
        "GENERATED CODE - produced by tool/generate_ast.py. do not edit by hand."
    )
    lines.append('"""')
    lines.append("from __future__ import annotations")
    lines.append("from abc import ABC, abstractmethod")
    lines.append("from dataclasses import dataclass")
    lines.append("from typing import Any")
    lines.append("from plox.token import Token")
    lines.append("")
    lines.append("")

    # Base class
    lines.append(f"class {base_name}(ABC):")
    lines.append("    @abstractmethod")
    lines.append(f"    def accept(self, visitor: {base_name}Visitor) -> Any:")
    lines.append("        raise NotImplementedError")
    lines.append("")
    lines.append("")

    # Visitor Interface
    class_names = [t.split(":")[0].strip() for t in types]
    lines.append(f"class {base_name}Visitor(ABC):")
    for class_name in class_names:
        method_name = f"visit_{class_name.lower()}_{base_name.lower()}"

        lines.append("    @abstractmethod")
        lines.append(
            f"    def {method_name}(self, {base_name.lower()}: {class_name}) -> Any:"
        )
        lines.append("        raise NotImplementedError")
        lines.append("")
    lines.append("")

    for type_def in types:
        class_name, fields_str = type_def.split(":")
        class_name = class_name.strip()
        field_list = [f.strip() for f in fields_str.strip().split(",")]

        lines.append("@dataclass(frozen=True)")
        lines.append(f"class {class_name}({base_name}):")
        for field in field_list:
            field_type, field_name = field.split(" ")
            lines.append(f"    {field_name}: {field_type}")
        lines.append("")
        method_name = f"visit_{class_name.lower()}_{base_name.lower()}"
        lines.append(f"    def accept(self, visitor: {base_name}Visitor) -> Any:")
        lines.append(f"        return visitor.{method_name}(self)")
        lines.append("")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {path}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: generate_ast.py <output_directory>", file=sys.stderr)
        sys.exit(64)

    output_dir = sys.argv[1]

    define_ast(
        output_dir,
        "Expr",
        [
            "Binary   : Expr left, Token operator, Expr right",
            "Grouping : Expr expression",
            "Literal  : Any value",
            "Unary    : Token operator, Expr right",
        ],
    )

    define_ast(
        output_dir,
        "Stmt",
        [
            "Expression : Expr expression",
            "Print      : Expr expression",
        ],
    )


if __name__ == "__main__":
    main()
