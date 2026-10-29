"""Part 10: compare static, ML and hybrid detection on every sample.

Inputs (all produced earlier, never edited by hand):
  dataset/metadata.csv                 labels, groups, kinds
  dataset/samples/...                  the frozen sample files
  results/ml_predictions_<target>.csv  out-of-fold ML predictions (train.py)

For each target this writes:
  results/eval_per_sample_<target>.csv   one row per sample, all four predictions
  results/eval_metrics_<target>.csv      TP/FP/TN/FN, precision, recall, F1, FPR
  results/eval_mcnemar_<target>.csv      exact McNemar tests (hybrid vs baselines)
  results/eval_disagreements_<target>.csv samples where static and ML disagree

Configurations (chapter 3.7.4):
  static              a rule fired anywhere in the file for that class
  ml                  the out-of-fold ML prediction (score >= T)
  hybrid_agreement    label is Critical          (PRIMARY result)
  hybrid_union        label is Critical/High/Medium (secondary result)

Run from the project root:  python src/evaluate.py
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

from dataset_io import TARGETS, load_metadata, read_source, write_csv
from static_analyzer import analyze_source

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ("static", "ml", "hybrid_agreement", "hybrid_union")
LABELS = ("Critical", "High", "Medium", "No finding")

# (configuration, baseline, is this the primary comparison?)
COMPARISONS = (
    ("hybrid_agreement", "static", True),
    ("hybrid_agreement", "ml", True),
    ("hybrid_union", "static", False),
    ("hybrid_union", "ml", False),
)


# --------------------------------------------------------------- metrics

def confusion(labels: list[int], preds: list[int]) -> dict[str, int]:
    counts = {"TP": 0, "FP": 0, "TN": 0, "FN": 0}
    for label, pred in zip(labels, preds):
        key = ("T" if label == pred else "F") + ("P" if pred else "N")
        counts[key] += 1
    return counts


def ratio(numerator: int, denominator: int) -> float | None:
    """None (shown as blank) when undefined, e.g. precision with no positives predicted."""
    return None if denominator == 0 else numerator / denominator


def metrics(labels: list[int], preds: list[int]) -> dict:
    c = confusion(labels, preds)
    precision = ratio(c["TP"], c["TP"] + c["FP"])
    recall = ratio(c["TP"], c["TP"] + c["FN"])
    if precision is None or recall is None or precision + recall == 0:
        f1 = 0.0 if c["TP"] == 0 and (c["FP"] or c["FN"]) else None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        **c,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": ratio(c["FP"], c["FP"] + c["TN"]),
    }


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from the discordant counts.

    b = samples the first method got right and the second got wrong,
    c = the reverse. Under "no difference" each discordant sample is a
    fair coin flip, so the p-value is a binomial tail. Identical to
    statsmodels' mcnemar(table, exact=True).
    """
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(labels: list[int], first: list[int], second: list[int]) -> dict:
    a = b = c = d = 0
    for label, p1, p2 in zip(labels, first, second):
        right1, right2 = p1 == label, p2 == label
        if right1 and right2:
            a += 1
        elif right1:
            b += 1
        elif right2:
            c += 1
        else:
            d += 1
    return {"both_right": a, "first_only_right": b, "second_only_right": c,
            "both_wrong": d, "discordant": b + c, "p_value": mcnemar_exact(b, c)}


# --------------------------------------------------------------- inputs

def load_ml_predictions(path: Path, sample_ids: list[str]) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = {row["sample_id"]: row for row in csv.DictReader(handle)}
    missing = [sid for sid in sample_ids if sid not in rows]
    extra = [sid for sid in rows if sid not in set(sample_ids)]
    if missing or extra:
        raise ValueError(
            f"{path}: predictions don't match metadata.csv "
            f"(missing {missing[:5]}, unexpected {extra[:5]}). Re-run train.py "
            f"after any dataset change."
        )
    return rows


def static_results(samples: list[dict]) -> dict[str, set[str]]:
    """sample_id -> set of vulnerability classes any rule fired for."""
    fired: dict[str, set[str]] = {}
    for sample in samples:
        findings = analyze_source(read_source(sample["file"]), str(sample["file"]))
        fired[sample["sample_id"]] = {f.vuln_class for f in findings}
    return fired


# -------------------------------------------------------------- evaluate

def evaluate_target(target: str, samples: list[dict], fired: dict[str, set[str]],
                    ml_rows: dict[str, dict], combine) -> dict:
    label_column, vuln_class = TARGETS[target]
    per_sample: list[dict] = []

    for sample in samples:
        sid = sample["sample_id"]
        rule = vuln_class in fired[sid]
        ml = ml_rows[sid]["pred"] == "1"
        hybrid_label = combine(rule, ml)
        if hybrid_label not in LABELS:
            raise ValueError(f"combine() returned {hybrid_label!r}; expected one of {LABELS}")

        row = {
            "sample_id": sid,
            "kind": sample.get("kind", ""),
            "group_id": sample["group_id"],
            "label": sample[label_column],
            "static": int(rule),
            "ml": int(ml),
            "ml_score": ml_rows[sid]["score"],
            "hybrid_label": hybrid_label,
            "hybrid_agreement": int(hybrid_label == "Critical"),
            "hybrid_union": int(hybrid_label in ("Critical", "High", "Medium")),
        }
        # Free consistency check of combine() against the definitions.
        if row["hybrid_agreement"] != int(rule and ml) or row["hybrid_union"] != int(rule or ml):
            raise AssertionError(
                f"{sid}: combine({rule}, {ml}) = {hybrid_label!r} does not match the "
                f"agreement/union definitions in chapter 3.7.4"
            )
        per_sample.append(row)

    labels = [row["label"] for row in per_sample]
    metric_rows = [
        {"configuration": name, **metrics(labels, [row[name] for row in per_sample])}
        for name in CONFIGS
    ]
    mcnemar_rows = [
        {"comparison": f"{first} vs {second}", "primary": "yes" if primary else "no",
         **compare(labels, [r[first] for r in per_sample], [r[second] for r in per_sample])}
        for first, second, primary in COMPARISONS
    ]
    disagreements = [row for row in per_sample if row["static"] != row["ml"]]
    return {"per_sample": per_sample, "metrics": metric_rows,
            "mcnemar": mcnemar_rows, "disagreements": disagreements}


def fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def print_report(target: str, result: dict) -> None:
    labels = [r["label"] for r in result["per_sample"]]
    print(f"\n=== {target.upper()}: {len(labels)} samples, {sum(labels)} positive ===")
    header = f"{'configuration':18} {'TP':>4} {'FP':>4} {'TN':>4} {'FN':>4} " \
             f"{'prec':>6} {'recall':>6} {'F1':>6} {'FPR':>6}"
    print(header)
    print("-" * len(header))
    for m in result["metrics"]:
        print(f"{m['configuration']:18} {m['TP']:>4} {m['FP']:>4} {m['TN']:>4} {m['FN']:>4} "
              f"{fmt(m['precision']):>6} {fmt(m['recall']):>6} {fmt(m['f1']):>6} {fmt(m['fpr']):>6}")
    print("\nMcNemar (exact): b = first right only, c = second right only")
    for t in result["mcnemar"]:
        mark = "*" if t["primary"] == "yes" else " "
        print(f" {mark} {t['comparison']:28} b={t['first_only_right']:<3} "
              f"c={t['second_only_right']:<3} p={t['p_value']:.4f}")
    print(f"\nStatic and ML disagree on {len(result['disagreements'])} sample(s); "
          f"see eval_disagreements_{target}.csv")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the four configurations (Part 10).")
    parser.add_argument("--metadata", default=PROJECT_ROOT / "dataset" / "metadata.csv", type=Path)
    parser.add_argument("--results", default=PROJECT_ROOT / "results", type=Path)
    parser.add_argument("--targets", nargs="+", choices=sorted(TARGETS), default=sorted(TARGETS))
    args = parser.parse_args(argv)

    from hybrid import combine  # Part 9

    samples = load_metadata(args.metadata)
    sample_ids = [s["sample_id"] for s in samples]
    fired = static_results(samples)

    for target in args.targets:
        ml_rows = load_ml_predictions(args.results / f"ml_predictions_{target}.csv", sample_ids)
        result = evaluate_target(target, samples, fired, ml_rows, combine)

        write_csv(args.results / f"eval_per_sample_{target}.csv", result["per_sample"])
        write_csv(args.results / f"eval_metrics_{target}.csv", [
            {k: (round(v, 4) if isinstance(v, float) else ("" if v is None else v))
             for k, v in row.items()} for row in result["metrics"]])
        write_csv(args.results / f"eval_mcnemar_{target}.csv", [
            {**row, "p_value": round(row["p_value"], 6)} for row in result["mcnemar"]])
        write_csv(args.results / f"eval_disagreements_{target}.csv", result["disagreements"],
                  ["sample_id", "kind", "group_id", "label", "static", "ml",
                   "ml_score", "hybrid_label"])
        print_report(target, result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
