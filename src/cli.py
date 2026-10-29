"""Part 11: command-line interface.

    python src/cli.py [--mode {static,ml,hybrid}] [--output report.json]
                      [--recursive] [--min-confidence {critical,high,medium}]
                      path [path ...]

Exit codes (FR16): 0 no findings, 1 findings reported, 2 invalid usage,
3 a required model file is missing or unreadable.

Modes:
  static  only the rule engine (no ML libraries needed)
  ml      only the classifiers, one result per analysis unit
  hybrid  both, combined per unit and class by hybrid.combine (default)
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

from dataset_io import TARGETS, read_source
from parser import Unit, find_python_files, split_into_units
from static_analyzer import analyze_source

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLASS_NAMES = {"SQLI": "SQL injection", "HCC": "Hard-coded credential"}
CONFIDENCE_ORDER = {"Critical": 0, "High": 1, "Medium": 2}
MIN_CONFIDENCE = {"critical": {"Critical"}, "high": {"Critical", "High"},
                  "medium": {"Critical", "High", "Medium"}}
ML_ONLY_REMEDIATION = {
    "SQLI": "Check whether user input reaches this unit's SQL text; use driver "
            "placeholders and pass values separately.",
    "HCC": "Check this unit for embedded secrets; load them from environment "
           "variables or a secret manager.",
}


class ModelError(RuntimeError):
    """A model file is missing or can't be used."""


# ------------------------------------------------------------------ ML

def load_models(models_dir: Path) -> dict[str, dict]:
    """Load models/<target>.joblib bundles written by train.py."""
    try:
        import joblib
    except ImportError as exc:
        raise ModelError("joblib/scikit-learn are not installed; use --mode static") from exc

    bundles = {}
    for target in TARGETS:
        path = models_dir / f"{target}.joblib"
        if not path.is_file():
            raise ModelError(f"model not found: {path} (run src/train.py first, or use --mode static)")
        try:
            bundles[target] = joblib.load(path)
        except Exception as exc:  # corrupted file, version mismatch
            raise ModelError(f"cannot load {path}: {exc}") from exc
    return bundles


def ml_flags(units: list[Unit], bundles: dict[str, dict]) -> dict[tuple[str, str], bool]:
    """(unit name, vuln class) -> True when score >= that model's threshold."""
    from feature_extractor import extract_features

    flags: dict[tuple[str, str], bool] = {}
    for unit in units:
        features = extract_features(unit.node)
        for target, bundle in bundles.items():
            names = bundle["feature_names"]
            missing = [n for n in names if n not in features]
            if missing:
                raise ModelError(
                    f"model '{target}' expects features {missing[:5]} that "
                    f"extract_features() no longer returns; retrain the model"
                )
            vector = [[float(features[n]) for n in names]]
            model = bundle["model"]
            column = list(model.classes_).index(1)
            score = float(model.predict_proba(vector)[0][column])
            flags[(unit.name, TARGETS[target][1])] = score >= bundle["threshold"]
    return flags


# ------------------------------------------------------------- per file

def enclosing_unit(units: list[Unit], line: int) -> str:
    """The smallest unit whose line range contains `line`.

    Findings are matched to units by line, not by the name the rule engine
    gives them, so the two components always agree on which unit is which.
    """
    containing = [u for u in units if u.start_line <= line <= u.end_line]
    if not containing:
        return "<module>"
    return min(containing, key=lambda u: u.end_line - u.start_line).name


def finding_record(finding, unit: str, confidence: str) -> dict:
    record = finding.to_dict()
    record["unit"] = unit
    record["confidence"] = confidence
    record["vulnerability"] = CLASS_NAMES[finding.vuln_class]
    return record


def scan_file(path: Path, mode: str, bundles: dict | None, combine) -> list[dict]:
    try:
        source = read_source(path)
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
        print(f"Warning: {path}: skipped ({type(exc).__name__}: {exc})", file=sys.stderr)
        return []

    units = split_into_units(path, tree)
    findings = analyze_source(source, str(path)) if mode in ("static", "hybrid") else []
    flags = ml_flags(units, bundles) if mode in ("ml", "hybrid") else {}

    records: list[dict] = []
    if mode == "static":
        for f in findings:
            records.append(finding_record(f, enclosing_unit(units, f.line), "Rule"))
        return records

    rule_hits: dict[tuple[str, str], list] = {}
    for f in findings:
        rule_hits.setdefault((enclosing_unit(units, f.line), f.vuln_class), []).append(f)

    for unit in units:
        for vuln_class in ("SQLI", "HCC"):
            hits = rule_hits.get((unit.name, vuln_class), [])
            ml_positive = flags.get((unit.name, vuln_class), False)

            if mode == "ml":
                label = "ML" if ml_positive else None
            else:
                label = combine(bool(hits), ml_positive)
                label = None if label == "No finding" else label

            if label is None:
                continue
            if hits:
                records.extend(finding_record(f, unit.name, label) for f in hits)
            else:
                # ML-only result: name the unit and class, never a score as proof (NFR6).
                records.append({
                    "vuln_class": vuln_class,
                    "vulnerability": CLASS_NAMES[vuln_class],
                    "rule_id": None,
                    "file": str(path),
                    "unit": unit.name,
                    "line": unit.start_line,
                    "snippet": "",
                    "message": "The classifier associates this unit with this "
                               "vulnerability class, but no rule matched. Review it manually.",
                    "remediation": ML_ONLY_REMEDIATION[vuln_class],
                    "confidence": label,
                })
    return records


# ----------------------------------------------------------------- main

def print_records(records: list[dict], mode: str) -> None:
    if not records:
        print("No findings.")
        return
    for r in records:
        rule = f" [{r['rule_id']}]" if r.get("rule_id") else ""
        print(f"{r['file']}:{r['line']}  {r['confidence'].upper()}  {r['vulnerability']}{rule}")
        print(f"    unit:   {r['unit']}")
        if r["snippet"]:
            print(f"    code:   {r['snippet'].strip().splitlines()[0]}")
        print(f"    why:    {r['message']}")
        print(f"    fix:    {r['remediation']}")
    counts: dict[str, int] = {}
    for r in records:
        counts[r["confidence"]] = counts.get(r["confidence"], 0) + 1
    summary = ", ".join(f"{n} {label}" for label, n in counts.items())
    print(f"\n{len(records)} finding(s) ({mode} mode): {summary}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Detect SQL injection and hard-coded credentials in Python code "
                    "with static rules, machine learning, or both.",
        epilog="Exit codes: 0 no findings, 1 findings, 2 invalid usage, 3 model error.",
    )
    parser.add_argument("paths", nargs="+", metavar="path", help="Python file(s) or folder(s)")
    parser.add_argument("--mode", choices=("static", "ml", "hybrid"), default="hybrid",
                        help="detection configuration (default: hybrid)")
    parser.add_argument("--output", type=Path, help="also write findings to this JSON file")
    parser.add_argument("--recursive", action="store_true", help="scan subfolders too")
    parser.add_argument("--min-confidence", choices=("critical", "high", "medium"),
                        default="medium", help="hybrid mode: lowest label to report (default: medium)")
    parser.add_argument("--models", type=Path, default=PROJECT_ROOT / "models",
                        help="folder with sqli.joblib and hcc.joblib")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    started = time.perf_counter()

    combine = None
    bundles = None
    try:
        if args.mode == "hybrid":
            from hybrid import combine  # Part 9
        if args.mode in ("ml", "hybrid"):
            bundles = load_models(args.models)
    except ModelError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3

    files: list[Path] = []
    for path in args.paths:
        files.extend(find_python_files(path, recursive=args.recursive))

    records: list[dict] = []
    try:
        for path in files:
            records.extend(scan_file(path, args.mode, bundles, combine))
    except ModelError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3

    if args.mode == "hybrid":
        allowed = MIN_CONFIDENCE[args.min_confidence]
        records = [r for r in records if r["confidence"] in allowed]
        records.sort(key=lambda r: (CONFIDENCE_ORDER[r["confidence"]], r["file"], r["line"]))
    else:
        records.sort(key=lambda r: (r["file"], r["line"]))

    print_records(records, args.mode)
    elapsed = time.perf_counter() - started
    print(f"Scanned {len(files)} file(s) in {elapsed:.2f}s.")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({
            "mode": args.mode,
            "files_scanned": len(files),
            "seconds": round(elapsed, 3),
            "findings": records,
        }, indent=2), encoding="utf-8")
        print(f"JSON report written to {args.output}")

    return 1 if records else 0


if __name__ == "__main__":
    sys.exit(main())
