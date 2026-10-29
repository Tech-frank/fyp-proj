from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class Unit:
    file: Path
    name: str
    node: ast.AST
    start_line: int
    end_line: int


def find_python_files(
    path: str | Path,
    *,
    recursive: bool = False,
) -> Iterator[Path]:
    """Accept a Python file or collect Python files from a folder."""
    path = Path(path)

    try:
        if path.is_file():
            if path.suffix == ".py":
                yield path
            else:
                print(f"Warning: {path}: not a .py file")
        elif path.is_dir():
            pattern = "**/*.py" if recursive else "*.py"
            for candidate in sorted(path.glob(pattern)):
                if candidate.is_file():
                    yield candidate
        else:
            print(f"Warning: {path}: file or folder does not exist")
    except OSError as exc:
        print(f"Warning: {path}: cannot access files: {exc}")


def read_and_parse(path: Path) -> ast.Module | None:
    """Return the parsed AST, or warn and skip an unreadable/invalid file."""
    try:
        source = path.read_text(encoding="utf-8")
        return ast.parse(source, filename=str(path))
    except UnicodeDecodeError as exc:
        print(f"Warning: {path}: invalid UTF-8: {exc}")
    except OSError as exc:
        print(f"Warning: {path}: cannot read file: {exc}")
    except SyntaxError as exc:
        print(f"Warning: {path}: syntax error: {exc}")

    return None


def line_span(node: ast.AST) -> tuple[int, int]:
    """Include decorators in a function or class's source span."""
    start = node.lineno
    decorators = getattr(node, "decorator_list", [])
    if decorators:
        start = min(start, *(decorator.lineno for decorator in decorators))

    end = getattr(node, "end_lineno", None) or node.lineno
    return start, end


def split_into_units(path: Path, tree: ast.Module) -> list[Unit]:
    """
    Split top-level functions and direct class methods into units.

    Nested functions stay inside their parent function/method unit.
    Other statements form a single <module> unit.
    """
    units: list[Unit] = []
    module_statements: list[ast.stmt] = []
    function_types = (ast.FunctionDef, ast.AsyncFunctionDef)

    def add_unit(name: str, node: ast.AST) -> None:
        start, end = line_span(node)
        units.append(Unit(path, name, node, start, end))

    for statement in tree.body:
        if isinstance(statement, function_types):
            add_unit(statement.name, statement)

        elif isinstance(statement, ast.ClassDef):
            remaining_body: list[ast.stmt] = []

            for member in statement.body:
                if isinstance(member, function_types):
                    add_unit(f"{statement.name}.{member.name}", member)
                else:
                    remaining_body.append(member)

            # Preserve class-level code and its class context without
            # including methods a second time in the module unit.
            class_node = ast.ClassDef(
                name=statement.name,
                bases=statement.bases,
                keywords=statement.keywords,
                body=remaining_body,
                decorator_list=statement.decorator_list,
            )
            if hasattr(statement, "type_params"):
                class_node.type_params = statement.type_params
            ast.copy_location(class_node, statement)
            module_statements.append(class_node)

        else:
            module_statements.append(statement)

    if module_statements:
        module_node = ast.Module(
            body=module_statements,
            type_ignores=tree.type_ignores,
        )
        spans = [line_span(statement) for statement in module_statements]
        units.append(
            Unit(
                file=path,
                name="<module>",
                node=module_node,
                start_line=min(start for start, _ in spans),
                end_line=max(end for _, end in spans),
            )
        )

    return sorted(units, key=lambda unit: (unit.start_line, unit.name))


def collect_units(
    path: str | Path,
    *,
    recursive: bool = False,
) -> list[Unit]:
    units: list[Unit] = []

    for file in find_python_files(path, recursive=recursive):
        tree = read_and_parse(file)
        if tree is not None:
            units.extend(split_into_units(file, tree))

    return units


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Split Python files into AST units.")
    parser.add_argument("path", help="Python file or folder")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include subfolders",
    )
    args = parser.parse_args()

    for unit in collect_units(args.path, recursive=args.recursive):
        print(
            f"{unit.file}: {unit.name} "
            f"(lines {unit.start_line}-{unit.end_line})"
        )