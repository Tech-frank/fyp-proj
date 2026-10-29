"""Part 7: turn an AST (a whole file or one analysis unit) into numbers.

    extract_features(node: ast.AST) -> dict[str, float]

Always returns the same 44 keys in the same order, all finite floats.

Independence from the rules (FR7): this module never imports or calls the
static analyzer. It also looks at code differently on purpose:

* Names are matched as plain substrings ("tokenizer" counts as token-like),
  where the rules match whole name parts. The model learns how much a
  credential-looking name is worth; it is not told the answer.
* Value features describe the string itself (length, spaces, character mix,
  entropy). The rules ignore what a string looks like, so these are where
  the model can disagree with a rule, e.g. "Enter your password" vs "x9$Kq2!".
* SQL features count shapes anywhere in the code, without following
  variables, where the rules follow a query through local variables.

Feature groups (chapter 4.4.1):
  14 AST structure, 10 SQL lexical, 11 credential lexical (as listed in the
  report) + 4 credential-value features + 5 SQL/logging context features.
"""
from __future__ import annotations

import ast
import math
import re
from collections import Counter

# ----------------------------------------------------------- vocabularies

PASSWORD_WORDS = ("password", "passwd", "pwd", "passphrase")
SECRET_WORDS = ("secret", "token", "credential", "auth")
KEY_WORDS = ("key",)
CREDENTIAL_WORDS = PASSWORD_WORDS + SECRET_WORDS + ("apikey", "api_key", "private_key", "access_key")

KNOWN_SECRET_PREFIXES = (
    "sk_live_", "sk_test_", "rk_live_", "pk_live_",     # Stripe
    "ghp_", "gho_", "ghu_", "ghs_", "github_pat_",      # GitHub
    "AKIA", "ASIA",                                     # AWS access key IDs
    "xoxb-", "xoxp-", "xoxa-",                          # Slack
    "AIza",                                             # Google API keys
    "-----BEGIN",                                       # PEM private keys
)

SQL_KEYWORDS = {
    "has_select": r"\bselect\b",
    "has_where": r"\bwhere\b",
    "has_insert": r"\binsert\s+into\b",
    "has_update": r"\bupdate\b\s+\w+\s+\bset\b",
    "has_delete": r"\bdelete\s+from\b",
    "has_from_kw": r"\bfrom\b",
    "has_order_by": r"\border\s+by\b",
}
SQL_ANY = re.compile(r"\b(select|insert\s+into|update\s+\w+\s+set|delete\s+from|where|order\s+by)\b", re.I)
SQL_PLACEHOLDER = re.compile(r"%[sd]")
URI_WITH_PASSWORD = re.compile(r"[a-z][a-z0-9+.\-]*://[^\s/:@]+:[^\s/@]+@", re.I)

EXECUTE_METHODS = {"execute", "executemany", "executescript"}
CONNECT_CALLS = {"connect", "create_engine", "MongoClient", "Redis", "StrictRedis"}
CONFIG_CALLS = {"load_dotenv", "dotenv_values", "ConfigParser", "safe_load", "load"}
LOG_METHODS = {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}

FEATURE_NAMES = (
    # 14 AST structure
    "total_nodes", "tree_depth", "num_functions", "num_calls", "num_assignments",
    "num_imports", "num_attributes", "num_comparisons", "num_subscripts",
    "num_string_literals", "num_joined_str", "num_format_calls", "num_concat_ops",
    "num_execute_calls",
    # 10 SQL lexical
    "has_select", "has_where", "has_insert", "has_update", "has_delete",
    "has_from_kw", "has_order_by", "has_sql_percent", "sql_str_count", "has_execute_call",
    # 11 credential lexical
    "has_password_id", "has_secret_id", "has_key_id", "has_credential_str",
    "has_env_access", "has_config_read", "num_string_assign", "has_connect_call",
    "has_known_prefix", "has_hardcoded_url", "cred_str_count",
    # 4 credential value
    "cred_value_max_len", "cred_value_has_space", "cred_value_char_classes",
    "cred_value_entropy",
    # 5 SQL / logging context
    "sql_dynamic_count", "execute_direct_dynamic", "execute_with_params",
    "num_log_or_print", "dynamic_string_logged",
)


# ---------------------------------------------------------------- helpers

def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _identifier(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.arg):
        return node.arg
    return None


def _has_word(name: str, words: tuple[str, ...]) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in words)


def _string_text(node: ast.AST) -> str:
    """All literal text inside a string expression (constant parts of
    f-strings, both sides of +, the template of % and .format())."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(_string_text(v) for v in node.values)
    if isinstance(node, ast.BinOp):
        return _string_text(node.left) + " " + _string_text(node.right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        return _string_text(node.func.value)
    return ""


def _is_dynamic_string(node: ast.AST) -> bool:
    """A string built from parts at run time: f-string with a value,
    + with a non-literal side, % on a string, or "...".format(...)."""
    if isinstance(node, ast.JoinedStr):
        return any(isinstance(v, ast.FormattedValue) for v in node.values)
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mod):
            return isinstance(node.left, (ast.Constant, ast.JoinedStr)) and bool(_string_text(node.left))
        if isinstance(node.op, ast.Add):
            sides = (node.left, node.right)
            has_text = any(_string_text(s) for s in sides)
            all_literal = all(isinstance(s, ast.Constant) for s in sides)
            return has_text and not all_literal
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        return bool(_string_text(node.func.value))
    return False


def _entropy(text: str) -> float:
    """Shannon entropy in bits per character: random secrets score high,
    words and sentences lower."""
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def _char_classes(text: str) -> int:
    return sum((
        any(c.islower() for c in text),
        any(c.isupper() for c in text),
        any(c.isdigit() for c in text),
        any(not c.isalnum() and not c.isspace() for c in text),
    ))


def _depth(node: ast.AST) -> int:
    deepest = 0
    stack = [(node, 1)]
    while stack:
        current, level = stack.pop()
        deepest = max(deepest, level)
        stack.extend((child, level + 1) for child in ast.iter_child_nodes(current))
    return deepest


def _assignment_pairs(node: ast.AST):
    """(target name, value node) for assignments, annotated assignments
    and keyword arguments: the places a credential is given a value."""
    for item in ast.walk(node):
        if isinstance(item, ast.Assign):
            for target in item.targets:
                name = _identifier(target)
                if name:
                    yield name, item.value
        elif isinstance(item, ast.AnnAssign) and item.value is not None:
            name = _identifier(item.target)
            if name:
                yield name, item.value
        elif isinstance(item, ast.Call):
            for keyword in item.keywords:
                if keyword.arg:
                    yield keyword.arg, keyword.value


# ------------------------------------------------------------ the function

def extract_features(node: ast.AST) -> dict[str, float]:
    nodes = list(ast.walk(node))
    calls = [n for n in nodes if isinstance(n, ast.Call)]
    strings = [n.value for n in nodes if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    lowered = [s.lower() for s in strings]
    identifiers = [name for n in nodes if (name := _identifier(n))]
    identifiers += [kw.arg for c in calls for kw in c.keywords if kw.arg]

    f: dict[str, float] = {}

    # --- AST structure
    f["total_nodes"] = len(nodes)
    f["tree_depth"] = _depth(node)
    f["num_functions"] = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) for n in nodes)
    f["num_calls"] = len(calls)
    f["num_assignments"] = sum(isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)) for n in nodes)
    f["num_imports"] = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in nodes)
    f["num_attributes"] = sum(isinstance(n, ast.Attribute) for n in nodes)
    f["num_comparisons"] = sum(isinstance(n, ast.Compare) for n in nodes)
    f["num_subscripts"] = sum(isinstance(n, ast.Subscript) for n in nodes)
    f["num_string_literals"] = len(strings)
    f["num_joined_str"] = sum(isinstance(n, ast.JoinedStr) for n in nodes)
    f["num_format_calls"] = (
        sum(_call_name(c) == "format" and isinstance(c.func, ast.Attribute) for c in calls)
        + sum(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and bool(_string_text(n.left)) for n in nodes)
    )
    f["num_concat_ops"] = sum(
        isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add)
        and bool(_string_text(n.left) or _string_text(n.right))
        for n in nodes
    )
    execute_calls = [c for c in calls if _call_name(c) in EXECUTE_METHODS]
    f["num_execute_calls"] = len(execute_calls)

    # --- SQL lexical (over every literal string fragment)
    for key, pattern in SQL_KEYWORDS.items():
        f[key] = float(any(re.search(pattern, s) for s in lowered))
    f["has_sql_percent"] = float(any(SQL_PLACEHOLDER.search(s) for s in strings))
    f["sql_str_count"] = sum(bool(SQL_ANY.search(s)) for s in strings)
    f["has_execute_call"] = float(bool(execute_calls))

    # --- credential lexical
    f["has_password_id"] = float(any(_has_word(i, PASSWORD_WORDS) for i in identifiers))
    f["has_secret_id"] = float(any(_has_word(i, SECRET_WORDS) for i in identifiers))
    f["has_key_id"] = float(any(_has_word(i, KEY_WORDS) for i in identifiers))

    cred_values = [
        value.value
        for name, value in _assignment_pairs(node)
        if _has_word(name, CREDENTIAL_WORDS)
        and isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value
    ]
    f["has_credential_str"] = float(bool(cred_values))
    f["has_env_access"] = float(
        any(isinstance(n, ast.Attribute) and n.attr in ("environ", "getenv") for n in nodes)
        or any(_call_name(c) == "getenv" for c in calls)
    )
    f["has_config_read"] = float(any(_call_name(c) in CONFIG_CALLS for c in calls))
    f["num_string_assign"] = sum(
        isinstance(n, (ast.Assign, ast.AnnAssign))
        and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)
        for n in nodes
    )
    f["has_connect_call"] = float(any(_call_name(c) in CONNECT_CALLS for c in calls))
    f["has_known_prefix"] = float(any(s.startswith(KNOWN_SECRET_PREFIXES) for s in strings))
    f["has_hardcoded_url"] = float(any(URI_WITH_PASSWORD.search(s) for s in strings))
    f["cred_str_count"] = len(cred_values)

    # --- credential value (what the assigned string looks like)
    f["cred_value_max_len"] = max((len(v) for v in cred_values), default=0)
    f["cred_value_has_space"] = float(any(re.search(r"\s", v) for v in cred_values))
    f["cred_value_char_classes"] = max((_char_classes(v) for v in cred_values), default=0)
    f["cred_value_entropy"] = round(max((_entropy(v) for v in cred_values), default=0.0), 6)

    # --- SQL / logging context (no variable tracking: that is the rules' job)
    dynamic = [n for n in nodes if _is_dynamic_string(n)]
    f["sql_dynamic_count"] = sum(bool(SQL_ANY.search(_string_text(n))) for n in dynamic)
    f["execute_direct_dynamic"] = float(any(c.args and _is_dynamic_string(c.args[0]) for c in execute_calls))
    f["execute_with_params"] = float(any(len(c.args) >= 2 for c in execute_calls))
    log_calls = [c for c in calls if _call_name(c) in LOG_METHODS or _call_name(c) == "print"]
    f["num_log_or_print"] = len(log_calls)
    f["dynamic_string_logged"] = float(any(
        any(_is_dynamic_string(a) for a in c.args) for c in log_calls
    ))

    return {name: float(f[name]) for name in FEATURE_NAMES}
