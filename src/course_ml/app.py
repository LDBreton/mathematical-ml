"""FastAPI scoring service for the churn deployment lesson."""

from __future__ import annotations

import os
from functools import lru_cache
from math import isfinite
from pathlib import Path
from typing import Literal, Mapping

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .train import FEATURES


class ChurnInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenure_months: int = Field(ge=0, le=120)
    monthly_charge: float = Field(ge=0, le=100_000, allow_inf_nan=False)
    support_calls: int = Field(ge=0, le=10_000)
    contract: Literal["monthly", "annual", "two_year"]


class ChurnPrediction(BaseModel):
    churn_probability: float = Field(ge=0, le=1)
    threshold: float = Field(gt=0, lt=1)
    prediction: int = Field(ge=0, le=1)


class ModelArtifactError(RuntimeError):
    """The configured model artifact is absent or malformed."""


@lru_cache(maxsize=4)
def _load_artifact(path: str) -> dict:
    artifact_path = Path(path)
    if not artifact_path.is_file():
        raise ModelArtifactError(f"Model artifact not found: {artifact_path}")
    try:
        artifact = joblib.load(artifact_path)
        if not isinstance(artifact, dict) or "pipeline" not in artifact or "metadata" not in artifact:
            raise ValueError("artifact must contain pipeline and metadata")
        pipeline = artifact["pipeline"]
        metadata = artifact["metadata"]
        if not callable(getattr(pipeline, "predict_proba", None)):
            raise ValueError("pipeline must provide predict_proba")
        if not isinstance(metadata, Mapping) or metadata.get("artifact_format") != 1:
            raise ValueError("metadata format is invalid")
        threshold = metadata.get("threshold")
        if (
            metadata.get("features") != FEATURES
            or metadata.get("contract_values") != ["monthly", "annual", "two_year"]
            or not isinstance(threshold, (int, float))
            or not isfinite(threshold)
            or not 0 < threshold < 1
        ):
            raise ValueError("model schema or threshold is invalid")
        probe = pd.DataFrame(
            [{"tenure_months": 0, "monthly_charge": 0.0, "support_calls": 0, "contract": "monthly"}],
            columns=FEATURES,
        )
        probabilities = np.asarray(pipeline.predict_proba(probe), dtype=float)
        if (
            probabilities.shape != (1, 2)
            or not np.isfinite(probabilities).all()
            or not np.isclose(probabilities.sum(), 1.0)
        ):
            raise ValueError("pipeline returned invalid binary probabilities")
        return artifact
    except Exception as exc:
        raise ModelArtifactError(f"Could not load a valid model artifact at {artifact_path}: {exc}") from exc


def _model_path() -> str:
    return os.environ.get("MODEL_PATH", "artifacts/churn.joblib")


app = FastAPI(title="Churn scoring API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Check both process liveness and whether the configured model can load."""
    try:
        _load_artifact(_model_path())
    except ModelArtifactError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ok", "model": "loaded"}


@app.post("/predict", response_model=ChurnPrediction)
def predict(payload: ChurnInput) -> ChurnPrediction:
    """Return the model's probability estimate and its threshold decision."""
    try:
        artifact = _load_artifact(_model_path())
    except ModelArtifactError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    row = pd.DataFrame([payload.model_dump()], columns=FEATURES)
    probability = float(artifact["pipeline"].predict_proba(row)[0, 1])
    threshold = float(artifact["metadata"]["threshold"])
    return ChurnPrediction(
        churn_probability=probability,
        threshold=threshold,
        prediction=int(probability >= threshold),
    )
