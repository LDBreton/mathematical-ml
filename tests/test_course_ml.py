from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from course_ml import app as api
from course_ml.app import ChurnInput
from course_ml.train import FEATURES, train_model


def _dataset(path, rows: int = 80) -> pd.DataFrame:
    index = np.arange(rows)
    contract = np.array(["monthly", "annual", "two_year"])[index % 3]
    tenure = (index * 7) % 65
    charge = 35.0 + (index * 11) % 120
    calls = (index * 3) % 8
    # A deterministic signal with overlap: short tenure and frequent support
    # contacts increase the probability of the positive class.
    logits = 1.8 - 0.055 * tenure + 0.35 * calls + 0.018 * (charge - 80) + (contract == "monthly") * 0.8
    churn = (logits > 2.6).astype(int)
    frame = pd.DataFrame(
        {
            "tenure_months": tenure,
            "monthly_charge": charge,
            "support_calls": calls,
            "contract": contract,
            "churn": churn,
        }
    )
    # Ensure both labels exist even if the generated pattern changes.
    frame.loc[0, "churn"] = 0
    frame.loc[1, "churn"] = 1
    frame.to_csv(path, index=False)
    return frame


@pytest.fixture
def trained(tmp_path):
    data_path = tmp_path / "churn.csv"
    artifact_path = tmp_path / "churn.joblib"
    _dataset(data_path)
    metadata = train_model(data_path, artifact_path, threshold=0.42)
    return data_path, artifact_path, metadata


def test_training_artifact_roundtrip_has_schema_metrics_and_same_predictions(trained):
    _, artifact_path, metadata = trained
    loaded = joblib.load(artifact_path)
    assert loaded["metadata"] == metadata
    assert metadata["features"] == FEATURES
    assert metadata["threshold"] == 0.42
    assert metadata["train_rows"] + metadata["test_rows"] == 80
    assert set(metadata["metrics"]) == {"accuracy", "precision", "recall", "f1", "roc_auc"}
    record = pd.DataFrame(
        [{"tenure_months": 8, "monthly_charge": 92.0, "support_calls": 4, "contract": "monthly"}],
        columns=FEATURES,
    )
    original = loaded["pipeline"].predict_proba(record)
    copied_path = artifact_path.with_name("copied.joblib")
    joblib.dump(loaded, copied_path)
    reloaded = joblib.load(copied_path)["pipeline"].predict_proba(record)
    np.testing.assert_allclose(original, reloaded, rtol=0, atol=0)


def test_api_health_and_prediction_use_saved_threshold(trained, monkeypatch):
    _, artifact_path, _ = trained
    monkeypatch.setenv("MODEL_PATH", str(artifact_path))
    api._load_artifact.cache_clear()
    client = TestClient(api.app)
    assert client.get("/health").json() == {"status": "ok", "model": "loaded"}
    response = client.post(
        "/predict",
        json={"tenure_months": 8, "monthly_charge": 92.0, "support_calls": 4, "contract": "monthly"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["threshold"] == 0.42
    assert 0 <= result["churn_probability"] <= 1
    assert result["prediction"] == int(result["churn_probability"] >= 0.42)
    artifact = joblib.load(artifact_path)
    expected = artifact["pipeline"].predict_proba(
        pd.DataFrame(
            [{"tenure_months": 8, "monthly_charge": 92.0, "support_calls": 4, "contract": "monthly"}],
            columns=FEATURES,
        )
    )[0, 1]
    assert result["churn_probability"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "payload",
    [
        {"tenure_months": 4, "monthly_charge": 60, "support_calls": 1, "contract": "quarterly"},
        {"tenure_months": -1, "monthly_charge": 60, "support_calls": 1, "contract": "monthly"},
        {"tenure_months": 4, "monthly_charge": 60, "support_calls": 1},
        {"tenure_months": 4, "monthly_charge": 60, "support_calls": 1, "contract": "annual", "admin": True},
        {"tenure_months": 4, "monthly_charge": 100_001, "support_calls": 1, "contract": "monthly"},
        {"tenure_months": 4, "monthly_charge": 60, "support_calls": 1.5, "contract": "monthly"},
    ],
)
def test_api_rejects_invalid_or_unexpected_input(payload, trained, monkeypatch):
    _, artifact_path, _ = trained
    monkeypatch.setenv("MODEL_PATH", str(artifact_path))
    api._load_artifact.cache_clear()
    response = TestClient(api.app).post("/predict", json=payload)
    assert response.status_code == 422


def test_api_reports_missing_model_as_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "missing.joblib"))
    api._load_artifact.cache_clear()
    client = TestClient(api.app)
    assert client.get("/health").status_code == 503
    assert client.post(
        "/predict",
        json={"tenure_months": 1, "monthly_charge": 20, "support_calls": 0, "contract": "monthly"},
    ).status_code == 503


@pytest.mark.parametrize("bad_value", [float("inf"), 100_001.0])
def test_training_rejects_nonfinite_and_out_of_range_numeric_values(tmp_path, bad_value):
    data_path = tmp_path / "bad.csv"
    frame = _dataset(data_path)
    frame.loc[3, "monthly_charge"] = bad_value
    frame.to_csv(data_path, index=False)
    with pytest.raises(ValueError, match="finite|ranges"):
        train_model(data_path, tmp_path / "model.joblib")


def test_training_rejects_noninteger_count_features(tmp_path):
    data_path = tmp_path / "bad.csv"
    frame = _dataset(data_path)
    frame["support_calls"] = frame["support_calls"].astype(float)
    frame.loc[3, "support_calls"] = 1.5
    frame.to_csv(data_path, index=False)
    with pytest.raises(ValueError, match="must be integers"):
        train_model(data_path, tmp_path / "model.joblib")


def test_api_schema_rejects_nonfinite_charge():
    with pytest.raises(ValidationError):
        ChurnInput.model_validate(
            {"tenure_months": 4, "monthly_charge": float("inf"), "support_calls": 1, "contract": "monthly"}
        )


@pytest.mark.parametrize("artifact_contents", [b"unreadable joblib", None])
def test_api_reports_malformed_or_unreadable_artifact_as_unavailable(
    tmp_path, monkeypatch, artifact_contents
):
    artifact_path = tmp_path / "broken.joblib"
    if artifact_contents is not None:
        artifact_path.write_bytes(artifact_contents)
    else:
        joblib.dump({"pipeline": object(), "metadata": {}}, artifact_path)
    monkeypatch.setenv("MODEL_PATH", str(artifact_path))
    api._load_artifact.cache_clear()
    assert TestClient(api.app).get("/health").status_code == 503
