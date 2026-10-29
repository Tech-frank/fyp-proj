import unittest

from findings import Finding
from hybrid import (
    OOFPrediction,
    build_evaluation_rows,
    combine,
    decide_unit,
)


def example_finding(file="sample.py", line=1):
    return Finding(
        vuln_class="HCC",
        rule_id="HCC001",
        file=file,
        unit="<module>",
        line=line,
        snippet='password = "example-secret"',
        message="Hardcoded credential.",
        remediation="Load the credential from an environment variable.",
        secrets=("example-secret",),
    )


class HybridTests(unittest.TestCase):
    def test_both_positive(self):
        self.assertEqual(combine(True, True), "Critical")

    def test_static_only(self):
        self.assertEqual(combine(True, False), "High")

    def test_ml_only(self):
        self.assertEqual(combine(False, True), "Medium")

    def test_both_negative(self):
        self.assertEqual(combine(False, False), "No finding")

    def test_preserves_multiple_static_findings(self):
        findings = [
            example_finding(line=1),
            example_finding(line=5),
        ]

        decisions = decide_unit(
            file="sample.py",
            unit="<module>",
            static_findings=findings,
            ml_scores={"HCC": 0.8, "SQLI": 0.1},
            threshold=0.5,
        )

        hcc = decisions[0]
        self.assertEqual(hcc.label, "Critical")
        self.assertEqual(
            [item.finding for item in hcc.findings],
            findings,
        )
        self.assertTrue(
            all(item.label == "Critical" for item in hcc.findings)
        )

    def test_ml_only_has_unit_decision_without_rule_findings(self):
        decisions = decide_unit(
            file="sample.py",
            unit="<module>",
            static_findings=[],
            ml_scores={"HCC": 0.9, "SQLI": 0.1},
            threshold=0.5,
        )

        self.assertEqual(decisions[0].label, "Medium")
        self.assertEqual(decisions[0].findings, ())

    def test_evaluation_consistency_for_all_four_cases(self):
        rows = build_evaluation_rows(
            static_findings=[
                example_finding(file="both.py"),
                example_finding(file="static_only.py"),
            ],
            oof_predictions=[
                OOFPrediction("both.py", "HCC", 0.9, fold=0),
                OOFPrediction("static_only.py", "HCC", 0.1, fold=1),
                OOFPrediction("ml_only.py", "HCC", 0.9, fold=2),
                OOFPrediction("neither.py", "HCC", 0.1, fold=3),
            ],
            threshold=0.5,
        )

        self.assertEqual(
            [row.label for row in rows],
            ["Critical", "High", "Medium", "No finding"],
        )

        for row in rows:
            self.assertEqual(row.union, row.static or row.ml)
            self.assertEqual(row.agreement, row.static and row.ml)

    def test_threshold_is_inclusive(self):
        decisions = decide_unit(
            file="sample.py",
            unit="<module>",
            static_findings=[],
            ml_scores={"HCC": 0.5, "SQLI": 0.1},
            threshold=0.5,
        )

        self.assertTrue(decisions[0].ml_positive)


if __name__ == "__main__":
    unittest.main()