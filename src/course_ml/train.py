"""Train and package a reproducible churn classifier for the deployment lesson."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["tenure_months", "monthly_charge", "support_calls"]
CATEGORICAL_FEATURES = ["contract"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "churn"
CONTRACTS = ["monthly", "annual", "two_year"]
DEFAULT_THRESHOLD = 0.5


def _load_data(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_csv(path)
    expected = set(FEATURES + [TARGET])
    missing = expected - set(frame.columns)
    extra = set(frame.columns) - expected
    if missing or extra:
        raise ValueError(
            f"Expected columns {sorted(expected)}; missing={sorted(missing)}, extra={sorted(extra)}"
        )
    if frame.empty:
        raise ValueError("Training data must contain at least one row")
    if frame[FEATURES + [TARGET]].isna().any().any():
        raise ValueError("Training data cannot contain missing values")
    unexpected_contracts = sorted(set(frame["contract"].astype(str)) - set(CONTRACTS))
    if unexpected_contracts:
        raise ValueError(f"Unknown contract values: {unexpected_contracts}")
    y_raw = frame[TARGET]
    if not set(pd.unique(y_raw)).issubset({0, 1, False, True}):
        raise ValueError("churn must contain only binary values 0 and 1")
    y = y_raw.astype(int)
    if y.nunique() != 2:
        raise ValueError("Training data must contain both churn classes")
    x = frame[FEATURES].copy()
    for column in NUMERIC_FEATURES:
        x[column] = pd.to_numeric(x[column], errors="raise")
    numeric = x[NUMERIC_FEATURES].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError("Numeric features must be finite")
    if (
        (x["tenure_months"] < 0).any()
        or (x["tenure_months"] > 120).any()
        or (x["monthly_charge"] < 0).any()
        or (x["monthly_charge"] > 100_000).any()
        or (x["support_calls"] < 0).any()
        or (x["support_calls"] > 10_000).any()
    ):
        raise ValueError("Numeric features are outside the API's accepted ranges")
    if not (x["tenure_months"] % 1 == 0).all() or not (x["support_calls"] % 1 == 0).all():
        raise ValueError("tenure_months and support_calls must be integers")
    return x, y


def build_pipeline() -> Pipeline:
    """Create preprocessing and classification as one deployable estimator."""
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # scikit-learn before 1.2
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
    preprocessing = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", encoder, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return Pipeline(
        [
            ("preprocess", preprocessing),
            ("classifier", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
        ]
    )


def train_model(
    data_path: str | Path,
    output_path: str | Path,
    *,
    threshold: float = DEFAULT_THRESHOLD,
    test_size: float = 0.25,
    track: bool = False,
) -> dict[str, Any]:
    """Fit on a training split, evaluate once on held-out data, and save artifact."""
    if not 0 < threshold < 1:
        raise ValueError("threshold must be strictly between 0 and 1")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be strictly between 0 and 1")
    x, y = _load_data(Path(data_path))
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42, stratify=y
    )
    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)
    metrics: dict[str, float] = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }
    metadata: dict[str, Any] = {
        "artifact_format": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "features": FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "contract_values": CONTRACTS,
        "target": TARGET,
        "positive_class": 1,
        "threshold": threshold,
        "metrics": metrics,
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "random_state": 42,
        "model": "logistic regression with standardized numeric and one-hot categorical features",
        "model_parameters": {"C": 1.0, "max_iter": 1000, "solver": "lbfgs", "class_weight": None},
        "data_sha256": hashlib.sha256(Path(data_path).read_bytes()).hexdigest(),
        "dependency_versions": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
    }
    artifact = {"pipeline": pipeline, "metadata": metadata}
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".joblib", delete=False) as handle:
            temporary_name = handle.name
        joblib.dump(artifact, temporary_name)
        os.replace(temporary_name, destination)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)

    if track:
        _track_run(metadata, pipeline, destination)
    return metadata


def _track_run(metadata: dict[str, Any], pipeline: Pipeline, artifact_path: Path) -> None:
    try:
        import mlflow
        import mlflow.sklearn
    except ImportError as exc:
        raise RuntimeError("MLflow tracking requested, but MLflow is not installed") from exc
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    experiment = mlflow.get_experiment_by_name("churn-deployment-lesson")
    if experiment is None:
        experiment_id = mlflow.create_experiment("churn-deployment-lesson")
    else:
        experiment_id = experiment.experiment_id
    with mlflow.start_run(experiment_id=experiment_id):
        mlflow.log_params(
            {
                "threshold": metadata["threshold"],
                "test_rows": metadata["test_rows"],
                "random_state": metadata["random_state"],
                **{
                    f"model_{key}": "none" if value is None else value
                    for key, value in metadata["model_parameters"].items()
                },
            }
        )
        mlflow.log_metrics(metadata["metrics"])
        mlflow.set_tag("data_sha256", metadata["data_sha256"])
        mlflow.set_tag("python_version", metadata["dependency_versions"]["python"])
        mlflow.set_tag("scikit_learn_version", metadata["dependency_versions"]["scikit_learn"])
        mlflow.set_tag("pandas_version", metadata["dependency_versions"]["pandas"])
        mlflow.set_tag("numpy_version", metadata["dependency_versions"]["numpy"])
        mlflow.log_artifact(str(artifact_path), artifact_path="deployment")
        input_example = pd.DataFrame(
            [{"tenure_months": 8, "monthly_charge": 92.0, "support_calls": 4, "contract": "monthly"}],
            columns=FEATURES,
        )
        signature = mlflow.models.infer_signature(input_example, pipeline.predict_proba(input_example))
        mlflow.sklearn.log_model(pipeline, name="model", signature=signature, input_example=input_example)
        mlflow.set_tag("lesson", "08_deployment")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/churn.csv", help="CSV with the documented feature schema")
    parser.add_argument("--output", default="artifacts/churn.joblib", help="path for the deployable model artifact")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="probability cutoff for positive churn")
    parser.add_argument("--test-size", type=float, default=0.25, help="fraction reserved for held-out evaluation")
    parser.add_argument("--track", action="store_true", help="record parameters, metrics, and model in local MLflow")
    args = parser.parse_args(argv)
    metadata = train_model(args.data, args.output, threshold=args.threshold, test_size=args.test_size, track=args.track)
    print(json.dumps({"artifact": str(args.output), "metrics": metadata["metrics"], "threshold": metadata["threshold"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
