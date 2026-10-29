from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

from findings import Finding


SINGLE_KEYWORDS = frozenset({
    "password", "passwd", "pwd", "secret", "token", "apikey",
})

MULTI_KEYWORDS = (
    ("api", "key"),
    ("access", "key"),
    ("private", "key"),
    ("auth", "key"),
    ("signing", "key"),
    ("encryption", "key"),
)

PLACEHOLDERS = frozenset({
    "password",
    "changeme",
    "<your-key-here>",
})

EXECUTE_METHODS = frozenset({
    "execute", "executemany", "executescript",
})


def name_parts(name: str) -> list[str]:
    """DB_PASSWORD -> db/password; APIKey -> api/key."""
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return [part.lower() for part in name.split("_") if part]


def is_credential_name(name: str) -> bool:
    parts = name_parts(name)

    if any(part in SINGLE_KEYWORDS for part in parts):
        return True

    return any(
        tuple(parts[index:index + len(keyword)]) == keyword
        for keyword in MULTI_KEYWORDS
        for index in range(len(parts) - len(keyword) + 1)
    )


def literal_secret(node: ast.AST | None) -> str | None:
    if not isinstance(node, ast.Constant):
        return None

    if not isinstance(node.value, str):
        return None

    value = node.value
    if not value.strip() or value.strip().lower() in PLACEHOLDERS:
        return None

    return value


def target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def uri_secrets(value: str) -> tuple[str, ...]:
    """Return encoded and decoded passwords from a connection URI."""
    if "://" not in value:
        return ()

    try:
        parsed = urlsplit(value)
        password = parsed.password
        username = parsed.username
    except ValueError:
        return ()

    if not username or not password:
        return ()

    decoded = unquote(password)
    if (
        not decoded.strip()
        or decoded.strip().lower() in PLACEHOLDERS
    ):
        return ()

    return tuple(dict.fromkeys((password, decoded)))


def resolve_expression(
    node: ast.expr,
    bindings: dict[str, ast.expr],
) -> ast.expr:
    """
    Substitute known local names at assignment/call time.

    Stored expressions are snapshots: a later reassignment does not
    retroactively change the expression assigned to another variable.
    """
    class Resolver(ast.NodeTransformer):
        def visit_Name(self, item: ast.Name) -> ast.expr:
            if isinstance(item.ctx, ast.Load) and item.id in bindings:
                return bindings[item.id]
            return item

    # Avoid changing the source AST or previously stored expressions.
    import copy

    return Resolver().visit(copy.deepcopy(node))


def static_string(node: ast.AST) -> str | None:
    """Recognise literal strings and concatenations of literal strings."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = static_string(node.left)
        right = static_string(node.right)
        if left is not None and right is not None:
            return left + right

    return None


def sql_rule(node: ast.AST) -> str | None:
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Add):
            # Literal-only concatenation is not dynamic.
            if static_string(node) is None:
                return "SQLI001"

        if isinstance(node.op, ast.Mod):
            if static_string(node.left) is not None:
                return "SQLI003"

    if isinstance(node, ast.JoinedStr):
        if any(
            isinstance(value, ast.FormattedValue)
            for value in node.values
        ):
            return "SQLI002"

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "format"
        and static_string(node.func.value) is not None
    ):
        return "SQLI004"

    return None


@dataclass
class PendingFinding:
    rule_id: str
    unit: str
    node: ast.AST
    message: str
    remediation: str


class RuleVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.unit = "<module>"
        self.class_path: list[str] = []
        self.function_depth = 0
        self.bindings: dict[str, ast.expr] = {}
        self.pending: list[PendingFinding] = []
        self.secrets: set[str] = set()

    def add(
        self,
        rule_id: str,
        node: ast.AST,
        message: str,
        remediation: str,
    ) -> None:
        self.pending.append(
            PendingFinding(
                rule_id, self.unit, node, message, remediation
            )
        )

    def credential(
        self,
        name: str | None,
        value: ast.AST | None,
        node: ast.AST,
        rule_id: str,
    ) -> None:
        secret = literal_secret(value)

        if name is None or not is_credential_name(name) or secret is None:
            return

        self.secrets.add(secret)
        self.add(
            rule_id,
            node,
            "A credential-named target receives a hardcoded string.",
            "Load the credential from an environment variable or "
            "a secret manager.",
        )

    def bind(self, target: ast.AST, value: ast.expr | None) -> None:
        if isinstance(target, ast.Name):
            if value is None:
                self.bindings.pop(target.id, None)
            else:
                self.bindings[target.id] = value

        elif isinstance(target, (ast.Tuple, ast.List)):
            # Invalidate unpacked names instead of guessing their values.
            for element in target.elts:
                self.bind(element, None)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self.credential(
                target_name(target), node.value, node, "HCC001"
            )

        # Visit the RHS before updating bindings: x = f(x) reads old x.
        self.generic_visit(node)

        value = resolve_expression(node.value, self.bindings)
        for target in node.targets:
            self.bind(target, value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.credential(
            target_name(node.target), node.value, node, "HCC001"
        )
        self.generic_visit(node)

        # A bare annotation does not assign a runtime value.
        if node.value is not None:
            self.bind(
                node.target,
                resolve_expression(node.value, self.bindings),
            )

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.generic_visit(node)

        if isinstance(node.target, ast.Name):
            previous = self.bindings.get(node.target.id)
            if previous is not None:
                value = ast.BinOp(
                    left=previous,
                    op=node.op,
                    right=resolve_expression(node.value, self.bindings),
                )
                self.bind(node.target, value)
            else:
                self.bind(node.target, None)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self.bind(target, None)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        for keyword in node.keywords:
            self.credential(
                keyword.arg,
                keyword.value,
                keyword,
                "HCC002",
            )

        called_name = None
        if isinstance(node.func, ast.Attribute):
            called_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            called_name = node.func.id

        if called_name in EXECUTE_METHODS and node.args:
            query = resolve_expression(node.args[0], self.bindings)
            rule_id = sql_rule(query)

            if rule_id is not None:
                self.add(
                    rule_id,
                    node,
                    "Dynamic values are inserted into SQL query text.",
                    "Use a constant SQL query with driver-supported "
                    "placeholders and pass values separately.",
                )

        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            secrets = uri_secrets(node.value)
            if secrets:
                self.secrets.update(secrets)
                self.add(
                    "HCC003",
                    node,
                    "A connection URI contains a hardcoded password.",
                    "Load connection credentials from an environment "
                    "variable or a secret manager.",
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_bindings = self.bindings
        self.bindings = {}
        self.class_path.append(node.name)

        try:
            self.generic_visit(node)
        finally:
            self.class_path.pop()
            self.bindings = old_bindings
            self.bindings.pop(node.name, None)

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        old_unit = self.unit
        old_bindings = self.bindings

        if self.function_depth == 0:
            self.unit = ".".join((*self.class_path, node.name))

        # Nested functions keep their parent's unit name, but their
        # assignments cannot affect the parent's bindings.
        self.bindings = {}
        self.function_depth += 1

        try:
            self.generic_visit(node)
        finally:
            self.function_depth -= 1
            self.unit = old_unit
            self.bindings = old_bindings
            self.bindings.pop(node.name, None)

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> None:
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        old_bindings = self.bindings
        self.bindings = {}

        try:
            self.generic_visit(node)
        finally:
            self.bindings = old_bindings


def analyze_source(source: str, file: str = "<string>") -> list[Finding]:
    tree = ast.parse(source, filename=file)
    visitor = RuleVisitor()
    visitor.visit(tree)

    # Finalise only after collecting credentials, so SQL findings and
    # messages also redact any detected credential appearing in them.
    secrets = tuple(visitor.secrets)
    findings: list[Finding] = []

    for item in visitor.pending:
        snippet = ast.get_source_segment(source, item.node) or ""

        findings.append(
            Finding(
                vuln_class=(
                    "HCC" if item.rule_id.startswith("HCC") else "SQLI"
                ),
                rule_id=item.rule_id,
                file=file,
                unit=item.unit,
                line=item.node.lineno,
                snippet=snippet,
                message=item.message,
                remediation=item.remediation,
                secrets=secrets,
            )
        )

    return sorted(
        findings,
        key=lambda finding: (
            finding.line, finding.rule_id, finding.unit
        ),
    )