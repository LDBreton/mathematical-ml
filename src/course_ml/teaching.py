"""Notebook housekeeping kept separate from the deployment lesson's main argument."""
from contextlib import contextmanager
import os
from pathlib import Path

from fastapi.testclient import TestClient

from . import app as api


@contextmanager
def local_prediction_client(artifact_path: str | Path):
    """Use a specific artifact for an in-process demo, then restore process state.

    This helper is for sequential notebook demonstrations, not concurrent servers.
    A running server should receive MODEL_PATH before process startup.
    """
    previous = os.environ.get("MODEL_PATH")
    try:
        os.environ["MODEL_PATH"] = str(artifact_path)
        api._load_artifact.cache_clear()
        with TestClient(api.app) as client:
            yield client
    finally:
        api._load_artifact.cache_clear()
        if previous is None:
            os.environ.pop("MODEL_PATH", None)
        else:
            os.environ["MODEL_PATH"] = previous
