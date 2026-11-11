"""Turn selected CredData Python lines into small, parseable, labelled samples.

- Only lines outside test/example/sample/demo/fixture/mock paths.
- T (true credential) -> hcc_label 1 (hcc_positive); F (false alarm) -> 0 (hcc_hard_negative).
- A sample is the smallest enclosing function (<= 40 lines), otherwise the
  smallest enclosing statement, dedented so it parses on its own.
- An F sample must contain no T or X (uncertain) line in its range.
- Every T value in the sample is obfuscated: letters and digits replaced by
  random ones of the same kind, punctuation kept (CredData's own approach).
- At most 2 samples per repository; group_id = the repository.
"""
import ast
import csv
import glob
import hashlib
import json
import os
import random
import textwrap
from pathlib import Path

random.seed(2026)
TARGET = {"T": 20, "F": 20}
PER_REPO = 2
MAX_LINES = 40
TEST_WORDS = ("test", "example", "sample", "demo", "fixture", "mock", "integration", "tasks.py")
T_EXCLUDE = {"UUID", "AWS S3 Bucket", "API"}
F_CATEGORIES = {"Password", "Token", "Key", "Secret", "Auth", "API", "Credential", "API:Token"}

needed = json.load(open("needed_repos.json"))
fetched = set(json.load(open("fetched.json")))

rows = []
for f in glob.glob("creddata/meta/*.csv"):
    rows += list(csv.DictReader(open(f, newline="", encoding="utf-8")))
by_file = {}
for r in rows:
    by_file.setdefault((r["RepoName"], Path(r["FilePath"]).stem), []).append(r)


def testy(p):
    return any(w in p.lower() for w in TEST_WORDS)


def file_index(repo):
    """file_id -> real path, using CredData's mapping sha256(relative path)[:8]."""
    full, _ = needed[repo]
    root = Path("repos") / repo
    index = {}
    for p in root.rglob("*.py"):
        if ".git" in p.parts or not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root).as_posix()
        index[hashlib.sha256(rel.encode()).hexdigest()[:8]] = (p, rel)
    return index


def obfuscate(value):
    out = []
    for ch in value:
        if ch.isdigit():
            out.append(random.choice("0123456789"))
        elif ch.isupper():
            out.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        elif ch.islower():
            out.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
        else:
            out.append(ch)
    return "".join(out)


def value_in_code_string(tree, line):
    """True when a non-docstring string literal sits on this line."""
    docstrings = {id(n.value) for n in ast.walk(tree)
                  if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    return any(
        isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings
        and n.lineno <= line <= n.end_lineno
        for n in ast.walk(tree)
    )


def enclosing(tree, line):
    """Smallest function (<= MAX_LINES) containing line, else smallest statement."""
    funcs, stmts = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt) and node.lineno <= line <= node.end_lineno:
            span = node.end_lineno - node.lineno + 1
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                if node.end_lineno - start + 1 <= MAX_LINES:
                    funcs.append((node.end_lineno - start, start, node.end_lineno))
            elif not isinstance(node, (ast.ClassDef, ast.If, ast.For, ast.While, ast.With, ast.Try)):
                stmts.append((span, node.lineno, node.end_lineno))
    pool = funcs or stmts
    if not pool:
        return None
    _, a, b = min(pool)
    return (a, b) if b - a + 1 <= MAX_LINES else None


candidates = {"T": [], "F": []}
for (repo, file_id), file_rows in by_file.items():
    if repo not in fetched:
        continue
    for r in file_rows:
        if r["FilePath"].endswith(".py") and not testy(r["FilePath"]) and r["GroundTruth"] in "TF":
            if r["GroundTruth"] == "F" and r["Category"] not in F_CATEGORIES:
                continue
            if r["GroundTruth"] == "T" and r["Category"] in T_EXCLUDE:
                continue
            candidates[r["GroundTruth"]].append(r)
for k in candidates:
    random.shuffle(candidates[k])

indexes, chosen, per_repo, seen_ranges = {}, [], {}, set()
for label in ("T", "F"):
    count = 0
    for r in candidates[label]:
        if count >= TARGET[label]:
            break
        repo = r["RepoName"]
        if per_repo.get(repo, 0) >= PER_REPO:
            continue
        if repo not in indexes:
            indexes[repo] = file_index(repo)
        hit = indexes[repo].get(Path(r["FilePath"]).stem)
        if not hit:
            continue
        path, rel = hit
        if testy(rel):
            continue  # the project's real path, not CredData's renamed one
        try:
            text = path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
            tree = ast.parse(text)
        except Exception:
            continue
        line = int(r["LineStart"])
        if label == "T" and not value_in_code_string(tree, line):
            continue
        span = enclosing(tree, line)
        if not span:
            continue
        a, b = span
        key = (repo, rel, a, b)
        if key in seen_ranges:
            continue
        in_range = [x for x in by_file[(repo, Path(r["FilePath"]).stem)]
                    if a <= int(x["LineStart"]) <= b]
        has_true = any(x["GroundTruth"] == "T" for x in in_range)
        has_unsure = any(x["GroundTruth"] == "X" for x in in_range)
        if label == "F" and (has_true or has_unsure):
            continue
        lines = text.split("\n")
        # obfuscate every true value in range (single-line values with positions)
        ok = True
        for x in sorted(in_range, key=lambda x: (int(x["LineStart"]), -int(x["ValueStart"] or -1))):
            if x["GroundTruth"] != "T":
                continue
            vs, ve = int(x["ValueStart"] or -1), int(x["ValueEnd"] or -1)
            if x["LineStart"] != x["LineEnd"] or not (0 <= vs < ve):
                ok = False
                break
            li = int(x["LineStart"]) - 1
            old = lines[li]
            lines[li] = old[:vs] + obfuscate(old[vs:ve]) + old[ve:]
        if not ok:
            continue
        snippet = textwrap.dedent("\n".join(lines[a - 1:b])).strip("\n") + "\n"
        if "execute(" in snippet:
            continue  # keep SQL injection out of the credential samples
        try:
            parsed = ast.parse(snippet)
        except SyntaxError:
            continue
        body = parsed.body
        if len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            continue  # a docstring on its own is not a realistic sample
        seen_ranges.add(key)
        per_repo[repo] = per_repo.get(repo, 0) + 1
        count += 1
        full, url = needed[repo]
        chosen.append({
            "label": label, "category": r["Category"], "repo": repo,
            "origin": f"{url}@{full[:12]}:{rel}#L{a}-L{b}",
            "snippet": snippet,
        })
    print(label, count, "chosen")

out = Path("additions/dataset/samples/external/creddata")
out.mkdir(parents=True, exist_ok=True)
meta = []
for i, c in enumerate(chosen, 1):
    kind = "positive" if c["label"] == "T" else "hard_negative"
    name = f"cd_{i:02d}_{kind}.py"
    (out / name).write_text(c["snippet"], encoding="utf-8")
    meta.append({
        "sample_id": f"cd_{i:02d}",
        "path": f"samples/external/creddata/{name}",
        "group_id": f"cd_{c['repo']}",
        "sqli_label": 0,
        "hcc_label": 1 if c["label"] == "T" else 0,
        "kind": f"hcc_{kind}",
        "source": "creddata",
        "cwe": "CWE-798" if c["label"] == "T" else "",
        "label_reason": (f"CredData ground truth T ({c['category']}); value obfuscated."
                         if c["label"] == "T" else
                         f"CredData ground truth F ({c['category']}): flagged by a scanner as a "
                         f"possible credential but judged not to be one."),
        "rule_expectation": "not assessed (external sample)",
        "reviewed": "",
        "origin": c["origin"],
    })
json.dump(meta, open("cd_rows.json", "w"), indent=1)
print(len(meta), "CredData samples from", len({m['group_id'] for m in meta}), "repositories")
