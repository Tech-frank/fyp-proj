"""Part 8: the cross-validation guarantees, on synthetic data (needs scikit-learn)."""
import numpy as np
import pytest

pytest.importorskip("sklearn")
from train import choose_threshold, cross_validate  # noqa: E402


def synthetic(n_groups=30, seed=0):
    rng = np.random.default_rng(seed)
    X, y, groups, ids = [], [], [], []
    for g in range(n_groups):
        label = g % 2
        for twin in range(2):  # two samples per group, like a positive and its variant
            X.append(rng.normal(loc=label * 1.5, size=4))
            y.append(label)
            groups.append(f"g{g}")
            ids.append(f"s{g}_{twin}")
    return np.array(X), np.array(y), np.array(groups), ids


def test_one_prediction_per_sample_and_no_group_leakage():
    X, y, groups, ids = synthetic()
    predictions, folds = cross_validate(X, y, groups, ids)
    assert sorted(p["sample_id"] for p in predictions) == sorted(ids)
    fold_of = {p["sample_id"]: p["fold"] for p in predictions}
    for group in set(groups):
        members = [sid for sid, g in zip(ids, groups) if g == group]
        assert len({fold_of[m] for m in members}) == 1, "a group was split across folds"


def test_deterministic():
    X, y, groups, ids = synthetic()
    assert cross_validate(X, y, groups, ids)[0] == cross_validate(X, y, groups, ids)[0]


def test_threshold_maximises_f1():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.4, 0.35, 0.9])
    assert choose_threshold(y, scores) == pytest.approx(0.35)
