"""Load and validate dataset/metadata.csv (shared by train.py and evaluate.py).

Required columns:
    sample_id   unique name for the sample, e.g. hcc_014
    path        file path relative to the folder that holds metadata.csv
    group_id    shared by a positive, its safe twin, and any template variants
    sqli_label  1 if the sample contains SQL injection, else 0
    hcc_label   1 if the sample contains a hard-coded credential, else 0

Optional columns (kept and passed through to reports):
    kind, source, cwe, label_reason
"""
from __future__ import annotations

import csv
from pathlib import Path

# target name -> (label column, vulnerability class used by the static engine)
TARGETS = {
    "sqli": ("sqli_label", "SQLI"),
    "hcc": ("hcc_label", "HCC"),
}

REQUIRED_COLUMNS = ("sample_id", "path", "group_id", "sqli_label", "hcc_label")


class DatasetError(ValueError):
    """Raised when metadata.csv is missing columns, values or files."""


def load_metadata(metadata_path: str | Path) -> list[dict]:
    """Return one dict per sample, with labels as ints and paths resolved.

    Fails loudly on any problem: a silent mistake here would corrupt
    every number in chapter 4.
    """
    metadata_path = Path(metadata_path)
    base = metadata_path.parent

    with metadata_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise DatasetError(f"{metadata_path}: missing columns {missing}")
        rows = list(reader)

    if not rows:
        raise DatasetError(f"{metadata_path}: no samples")

    samples: list[dict] = []
    seen: set[str] = set()
    problems: list[str] = []

    for line_no, row in enumerate(rows, start=2):
        sample_id = (row.get("sample_id") or "").strip()
        where = f"line {line_no} ({sample_id or 'no sample_id'})"

        if not sample_id:
            problems.append(f"{where}: empty sample_id")
            continue
        if sample_id in seen:
            problems.append(f"{where}: duplicate sample_id")
        seen.add(sample_id)

        if not (row.get("group_id") or "").strip():
            problems.append(f"{where}: empty group_id")

        labels = {}
        for column in ("sqli_label", "hcc_label"):
            value = (row.get(column) or "").strip()
            if value not in ("0", "1"):
                problems.append(f"{where}: {column} must be 0 or 1, got {value!r}")
            else:
                labels[column] = int(value)

        file_path = base / (row.get("path") or "").strip()
        if not file_path.is_file():
            problems.append(f"{where}: file not found: {file_path}")

        sample = {key: (value or "").strip() for key, value in row.items() if key}
        sample.update(labels)
        sample["file"] = file_path
        samples.append(sample)

    if problems:
        shown = "\n  ".join(problems[:20])
        more = f"\n  ... and {len(problems) - 20} more" if len(problems) > 20 else ""
        raise DatasetError(f"{metadata_path} has {len(problems)} problem(s):\n  {shown}{more}")

    return samples


def read_source(path: str | Path) -> str:
    """Read a Python file as text. utf-8-sig drops a Windows byte-order mark."""
    return Path(path).read_text(encoding="utf-8-sig")


def write_csv(path: str | Path, rows: list[dict], columns: list[str] | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
