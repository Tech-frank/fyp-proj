"""Part 8: train the classifiers with grouped, nested cross-validation.

For each target (sqli, hcc) this produces:

  results/features.csv                one row of features per sample
  results/ml_predictions_<target>.csv one OUT-OF-FOLD prediction per sample:
                                      made by a model that never saw it
  results/ml_folds_<target>.csv       per fold: chosen model, params, threshold
  models/<target>.joblib              the model the CLI ships with

How a prediction is made for the samples in one outer test fold:
  1. Only the other four folds (the outer training part) are used.
  2. Inside them, an inner grouped cross-validation compares Logistic
     Regression and Random Forest (small grids) by F1 and keeps the better.
  3. The threshold T is the value that maximises F1 on the inner
     out-of-fold scores of that chosen model (ties: closest to 0.5).
  4. The chosen model is refitted on the whole outer training part and
     scores the outer test fold; prediction = score >= T.
Groups (group_id) never straddle a train/test boundary, at either level.

The shipped model (models/<target>.joblib) is the same procedure applied
to all samples. Cross-validation estimates how well the PROCEDURE works;
evaluation must use the out-of-fold predictions, never the shipped model.

Run from the project root:
    python src/train.py
    python src/train.py --metadata dataset/metadata.csv --targets hcc
"""
from __future__ import annotations

import argparse
import math
import platform
import sys
from pathlib import Path

import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedGroupKFold,
    cross_val_predict,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from dataset_io import TARGETS, load_metadata, read_source, write_csv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED = 42
OUTER_FOLDS = 5
INNER_FOLDS = 3


# ---------------------------------------------------------------- models

def candidate_models() -> dict[str, tuple[object, dict]]:
    """The two model families compared inside every fold, with tiny grids.

    Grids are kept small on purpose: with ~200 samples, a large search
    mostly fits noise in the inner folds.
    """
    return {
        "logistic_regression": (
            Pipeline([
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(
                    class_weight="balanced", max_iter=5000, random_state=SEED,
                )),
            ]),
            {"clf__C": [0.1, 1.0, 10.0]},
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=200, class_weight="balanced", random_state=SEED,
            ),
            {"max_depth": [None, 5], "min_samples_leaf": [1, 3]},
        ),
    }


def build_model(name: str, params: dict):
    estimator, _ = candidate_models()[name]
    return clone(estimator).set_params(**params)


def positive_scores(model, X: np.ndarray) -> np.ndarray:
    """Probability of class 1, whichever column sklearn put it in."""
    column = list(model.classes_).index(1)
    return model.predict_proba(X)[:, column]


# ------------------------------------------------------------ thresholds

def f1_at(y: np.ndarray, scores: np.ndarray, threshold: float) -> float:
    predicted = scores >= threshold
    tp = int(np.sum(predicted & (y == 1)))
    fp = int(np.sum(predicted & (y == 0)))
    fn = int(np.sum(~predicted & (y == 1)))
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


def choose_threshold(y: np.ndarray, scores: np.ndarray) -> float:
    """Threshold that maximises F1; ties go to the value closest to 0.5.

    Fixed in chapter 3 before any result is seen. Candidates are the
    observed scores themselves (every distinct cut point), plus 0.5.
    """
    if not np.any(y == 1):
        raise ValueError("cannot choose a threshold: no positive samples")
    candidates = sorted(set(float(s) for s in scores) | {0.5})
    return max(
        candidates,
        key=lambda t: (round(f1_at(y, scores, t), 12), -abs(t - 0.5), -t),
    )


# ------------------------------------------------------------ splitting

def grouped_folds(y: np.ndarray, groups: np.ndarray, wanted: int, level: str) -> StratifiedGroupKFold:
    """A StratifiedGroupKFold with as many folds as the data can support.

    Every fold needs at least one positive and one negative group, so the
    number of folds can't exceed the number of groups in either class.
    """
    positive_groups = len(set(groups[y == 1]))
    negative_groups = len(set(groups[y == 0]))
    n_splits = min(wanted, positive_groups, negative_groups)
    if n_splits < 2:
        raise ValueError(
            f"{level} cross-validation needs at least 2 positive and 2 negative "
            f"groups; found {positive_groups} positive and {negative_groups} "
            f"negative groups. Add more samples (with different group_ids)."
        )
    if n_splits < wanted:
        print(f"  note: {level} CV uses {n_splits} folds (not {wanted}): "
              f"only {min(positive_groups, negative_groups)} groups in the smaller class")
    return StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=SEED)


def select_model(X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    """Steps 2–3 of the procedure, using ONLY the data passed in."""
    cv = grouped_folds(y, groups, INNER_FOLDS, "inner")

    best = None
    for name, (estimator, grid) in candidate_models().items():
        search = GridSearchCV(estimator, grid, scoring="f1", cv=cv, refit=False)
        search.fit(X, y, groups=groups)
        score = float(search.best_score_)
        if math.isnan(score):
            score = 0.0
        # Strictly greater: on a tie the simpler model (listed first) wins.
        if best is None or score > best["inner_f1"]:
            best = {"model": name, "params": search.best_params_, "inner_f1": score}

    model = build_model(best["model"], best["params"])
    inner_scores = cross_val_predict(
        model, X, y, groups=groups, cv=cv, method="predict_proba",
    )[:, 1]
    best["threshold"] = choose_threshold(y, inner_scores)
    return best


# ------------------------------------------------------------- features

def build_feature_table(samples: list[dict]) -> tuple[np.ndarray, list[str]]:
    """Run Part 7's extract_features on every sample file.

    Training and the CLI call the same function, so a sample is described
    identically in both. Imported here, not at the top, so the CV code can
    be tested before Part 7 exists.
    """
    import ast

    from feature_extractor import extract_features

    rows: list[dict] = []
    for sample in samples:
        tree = ast.parse(read_source(sample["file"]), filename=str(sample["file"]))
        features = extract_features(tree)
        rows.append({name: float(value) for name, value in features.items()})

    names = list(rows[0])
    for sample, row in zip(samples, rows):
        if set(row) != set(names):
            raise ValueError(
                f"{sample['sample_id']}: feature names differ from the first sample's "
                f"(extract_features must always return the same keys)"
            )
    X = np.array([[row[name] for name in names] for row in rows], dtype=float)
    if not np.all(np.isfinite(X)):
        bad = sorted({samples[i]["sample_id"] for i in np.argwhere(~np.isfinite(X))[:, 0]})
        raise ValueError(f"NaN or infinite feature values in: {bad}")
    return X, names


# ------------------------------------------------------------- training

def cross_validate(
    X: np.ndarray, y: np.ndarray, groups: np.ndarray, sample_ids: list[str],
) -> tuple[list[dict], list[dict]]:
    """Return (one out-of-fold prediction per sample, one summary per fold)."""
    outer = grouped_folds(y, groups, OUTER_FOLDS, "outer")
    predictions: list[dict] = []
    folds: list[dict] = []

    for fold, (train_idx, test_idx) in enumerate(outer.split(X, y, groups), start=1):
        leaked = set(groups[train_idx]) & set(groups[test_idx])
        if leaked:
            raise AssertionError(f"fold {fold}: group(s) in both train and test: {sorted(leaked)}")

        choice = select_model(X[train_idx], y[train_idx], groups[train_idx])
        model = build_model(choice["model"], choice["params"]).fit(X[train_idx], y[train_idx])
        scores = positive_scores(model, X[test_idx])

        for index, score in zip(test_idx, scores):
            predictions.append({
                "sample_id": sample_ids[index],
                "fold": fold,
                "label": int(y[index]),
                "score": round(float(score), 6),
                "threshold": round(choice["threshold"], 6),
                "pred": int(score >= choice["threshold"]),
                "model": choice["model"],
            })
        folds.append({
            "fold": fold,
            "model": choice["model"],
            "params": str(choice["params"]),
            "threshold": round(choice["threshold"], 6),
            "inner_f1": round(choice["inner_f1"], 4),
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "test_positives": int(y[test_idx].sum()),
        })
        print(f"  fold {fold}: {choice['model']} {choice['params']} "
              f"T={choice['threshold']:.3f} test={len(test_idx)}")

    ids = [row["sample_id"] for row in predictions]
    if sorted(ids) != sorted(sample_ids) or len(set(ids)) != len(ids):
        raise AssertionError("every sample must get exactly one out-of-fold prediction")
    predictions.sort(key=lambda row: sample_ids.index(row["sample_id"]))
    return predictions, folds


def train_shipped_model(X, y, groups, feature_names: list[str], target: str) -> dict:
    """The same selection procedure on ALL samples, for the CLI to use."""
    choice = select_model(X, y, groups)
    model = build_model(choice["model"], choice["params"]).fit(X, y)
    return {
        "target": target,
        "model": model,
        "model_name": choice["model"],
        "params": choice["params"],
        "threshold": choice["threshold"],
        "feature_names": feature_names,
        "n_samples": int(len(y)),
        "versions": {
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
        },
        "seed": SEED,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cross-validated training (Part 8).")
    parser.add_argument("--metadata", default=PROJECT_ROOT / "dataset" / "metadata.csv", type=Path)
    parser.add_argument("--results", default=PROJECT_ROOT / "results", type=Path)
    parser.add_argument("--models", default=PROJECT_ROOT / "models", type=Path)
    parser.add_argument("--targets", nargs="+", choices=sorted(TARGETS), default=sorted(TARGETS))
    args = parser.parse_args(argv)

    import joblib

    samples = load_metadata(args.metadata)
    print(f"{len(samples)} samples from {args.metadata}")
    X, feature_names = build_feature_table(samples)
    sample_ids = [s["sample_id"] for s in samples]
    groups = np.array([s["group_id"] for s in samples])

    feature_rows = [
        {"sample_id": sid, **dict(zip(feature_names, row))} for sid, row in zip(sample_ids, X)
    ]
    write_csv(args.results / "features.csv", feature_rows, ["sample_id", *feature_names])

    for target in args.targets:
        label_column, _ = TARGETS[target]
        y = np.array([s[label_column] for s in samples], dtype=int)
        print(f"\n[{target}] {int(y.sum())} positive / {int((y == 0).sum())} negative")

        predictions, folds = cross_validate(X, y, groups, sample_ids)
        write_csv(args.results / f"ml_predictions_{target}.csv", predictions)
        write_csv(args.results / f"ml_folds_{target}.csv", folds)

        thresholds = [f["threshold"] for f in folds]
        if max(thresholds) - min(thresholds) > 0.3:
            print(f"  warning: thresholds vary a lot across folds ({min(thresholds):.2f}–"
                  f"{max(thresholds):.2f}); the model is unstable at this data size. "
                  f"Report this in chapter 4.")

        bundle = train_shipped_model(X, y, groups, feature_names, target)
        args.models.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, args.models / f"{target}.joblib")
        print(f"  shipped model: {bundle['model_name']} T={bundle['threshold']:.3f} "
              f"-> {args.models / (target + '.joblib')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
