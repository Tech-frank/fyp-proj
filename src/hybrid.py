"""Part 9: combine the rule engine and the classifiers into one label.

    combine(static_positive, ml_positive) -> "Critical" | "High" | "Medium" | "No finding"

                    ML flags it    ML doesn't
    rule hit        Critical       High
    no rule hit     Medium         No finding

Critical is the "agreement" configuration and any of the three labels is the
"union" configuration (chapter 3.7.4). cli.py applies this per analysis unit;
evaluate.py applies it per sample using out-of-fold ML predictions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from findings import Finding

LABELS = ("Critical", "High", "Medium", "No finding")
VULN_CLASSES = ("HCC", "SQLI")


def combine(static_positive: bool, ml_positive: bool) -> str:
    """The hybrid decision table."""
    if static_positive and ml_positive:
        return "Critical"
    if static_positive:
        return "High"
    if ml_positive:
        return "Medium"
    return "No finding"


@dataclass(frozen=True)
class LabelledFinding:
    """One rule finding carrying the label of the unit decision it belongs to."""
    finding: Finding
    label: str


@dataclass(frozen=True)
class UnitDecision:
    """The hybrid result for one (file, unit, vulnerability class)."""
    file: str
    unit: str
    vuln_class: str
    static_positive: bool
    ml_positive: bool
    ml_score: float
    label: str
    findings: tuple[LabelledFinding, ...]


def decide_unit(
    *,
    file: str,
    unit: str,
    static_findings: Iterable[Finding],
    ml_scores: Mapping[str, float],
    threshold: float,
) -> list[UnitDecision]:
    """One decision per vulnerability class (HCC, then SQLI) for a unit.

    `static_findings` are the rule findings already assigned to this unit.
    The threshold is inclusive: a score equal to it counts as positive.
    Every rule finding is kept, so three hits give three labelled findings.
    An ML-only decision has no findings: there is no line-level evidence.
    """
    static_findings = list(static_findings)
    decisions = []
    for vuln_class in VULN_CLASSES:
        hits = [f for f in static_findings if f.vuln_class == vuln_class]
        score = float(ml_scores.get(vuln_class, 0.0))
        ml_positive = score >= threshold
        label = combine(bool(hits), ml_positive)
        decisions.append(UnitDecision(
            file=file,
            unit=unit,
            vuln_class=vuln_class,
            static_positive=bool(hits),
            ml_positive=ml_positive,
            ml_score=score,
            label=label,
            findings=tuple(LabelledFinding(f, label) for f in hits),
        ))
    return decisions


@dataclass(frozen=True)
class OOFPrediction:
    """An out-of-fold ML prediction for one sample file and class."""
    file: str
    vuln_class: str
    score: float
    fold: int


@dataclass(frozen=True)
class EvaluationRow:
    file: str
    vuln_class: str
    fold: int
    score: float
    static: bool
    ml: bool
    label: str
    agreement: bool
    union: bool


def build_evaluation_rows(
    *,
    static_findings: Iterable[Finding],
    oof_predictions: Iterable[OOFPrediction],
    threshold: float,
) -> list[EvaluationRow]:
    """One row per out-of-fold prediction, in the order given."""
    fired = {(f.file, f.vuln_class) for f in static_findings}
    rows = []
    for p in oof_predictions:
        static = (p.file, p.vuln_class) in fired
        ml = p.score >= threshold
        label = combine(static, ml)
        rows.append(EvaluationRow(
            file=p.file,
            vuln_class=p.vuln_class,
            fold=p.fold,
            score=p.score,
            static=static,
            ml=ml,
            label=label,
            agreement=label == "Critical",
            union=label != "No finding",
        ))
    return rows
