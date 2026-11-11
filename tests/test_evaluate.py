"""Part 10: metric and McNemar arithmetic, checked against hand-worked values."""
import pytest

from evaluate import compare, mcnemar_exact, metrics, metrics_by_source


def test_metrics_hand_worked():
    labels = [1, 1, 1, 0, 0, 0, 0]
    preds = [1, 1, 0, 1, 0, 0, 0]
    m = metrics(labels, preds)
    assert (m["TP"], m["FP"], m["TN"], m["FN"]) == (2, 1, 3, 1)
    assert m["precision"] == pytest.approx(2 / 3)
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["f1"] == pytest.approx(2 / 3)
    assert m["fpr"] == pytest.approx(1 / 4)


def test_precision_undefined_when_nothing_predicted():
    m = metrics([1, 0], [0, 0])
    assert m["precision"] is None and m["recall"] == 0 and m["f1"] == 0


def test_mcnemar_exact_known_values():
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(6, 0) == pytest.approx(2 / 64)      # 0.03125
    assert mcnemar_exact(5, 0) == pytest.approx(2 / 32)      # 0.0625: 5 is not enough
    assert mcnemar_exact(3, 3) == 1.0


def test_compare_counts_right_and_wrong_not_yes_and_no():
    labels = [1, 0, 1, 0]
    first = [1, 0, 0, 1]    # right, right, wrong, wrong
    second = [0, 0, 0, 0]   # wrong, right, wrong, right
    result = compare(labels, first, second)
    assert (result["both_right"], result["first_only_right"],
            result["second_only_right"], result["both_wrong"]) == (1, 1, 1, 1)


def test_metrics_split_by_source():
    rows = []
    for source, label, pred in [("ai-drafted", 1, 1), ("ai-drafted", 0, 0),
                                ("creddata", 1, 0), ("creddata", 0, 1), ("securityeval", 1, 1)]:
        rows.append({"source": source, "label": label, "static": pred, "ml": pred,
                     "hybrid_agreement": pred, "hybrid_union": pred})
    by = {(r["group"], r["configuration"]): r for r in metrics_by_source(rows)}
    assert by[("synthetic", "static")]["f1"] == 1.0
    assert by[("external", "static")]["samples"] == 3
    assert by[("external:creddata", "static")]["FP"] == 1
    assert by[("external:securityeval", "static")]["TP"] == 1
