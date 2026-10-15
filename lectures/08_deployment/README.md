# Lecture 08 — From a statistical model to a prediction service

This lesson turns a binary classifier into a small, inspectable deployment unit. It uses a synthetic customer churn table with features `tenure_months`, `monthly_charge`, `support_calls`, and `contract`, and a binary target `churn`. The fitted object is a scikit-learn `Pipeline`: numeric standardization, categorical one-hot encoding, and logistic regression travel together in one artifact.

From the repository root, train and save the model with:

```console
python -m course_ml.train --data data/churn.csv --output artifacts/churn.joblib
```

The command holds out a stratified test set, reports accuracy, precision, recall, F1, and ROC AUC, and saves the pipeline plus metadata. The metadata records the feature schema, target meaning, threshold, split sizes, random seed, and held-out metrics. `--threshold 0.35` changes the rule that turns probability into a class label. It does not refit the probability model. The default threshold is 0.5.

To record a local experiment, add `--track`. MLflow is included in the course environment:

```console
python -m course_ml.train --data data/churn.csv --output artifacts/churn.joblib --track
```

MLflow stores run parameters and held-out metrics in a local SQLite database named `mlflow.db`; model files and other artifacts go to its local artifact store. Set `MLFLOW_TRACKING_URI` to use another tracking store. Each run also records the data file's SHA-256 digest, Python and numerical-library versions, logistic regression settings, a model signature, and a sample input. The digest identifies the exact CSV bytes used for training. Tracking makes experiments easier to compare; it does not establish that the model is statistically sound. Keep the source revision alongside a run when reproducing a result.

Browse the local experiment database with:

```console
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1
```

The UI listens on port 5000 by default. Binding to `127.0.0.1` keeps this teaching interface on the local machine.

The FastAPI service reads `MODEL_PATH`, which defaults to `artifacts/churn.joblib`. To serve locally, train first and start Uvicorn:

```console
MODEL_PATH=artifacts/churn.joblib python -m uvicorn course_ml.app:app --reload --port 8001
```

On PowerShell, set the variable for the current shell and run Uvicorn as a module:

```powershell
$env:MODEL_PATH = "artifacts/churn.joblib"
python -m uvicorn course_ml.app:app --reload --port 8001
```

`GET /health` checks whether the configured model can load. `POST /predict` accepts a JSON object with the four feature fields and returns a churn probability, the saved threshold, and the resulting 0/1 decision. The application code never fits a model while serving requests.

You can exercise the API without opening a network port:

```python
from fastapi.testclient import TestClient
from course_ml.app import app

client = TestClient(app)
client.get("/health").json()
client.post("/predict", json={
    "tenure_months": 8,
    "monthly_charge": 92.0,
    "support_calls": 4,
    "contract": "monthly",
}).json()
```

## Statistical choices and limits

For a feature vector \(x\), logistic regression models \(p(x)=\Pr(Y=1\mid X=x)=\sigma(\beta_0+\beta^T z(x))\), where \(z\) is the fitted preprocessing map and \(\sigma(t)=(1+e^{-t})^{-1}\). Standardization puts numeric coordinates on comparable scales. One-hot encoding represents contract categories without pretending that `monthly < annual < two_year` is a numeric distance. The whole map is fitted on the training subset, so held-out examples do not influence means, variances, or category encoding.

The default class decision is \(\hat y=1\{p(x)\geq \tau\}\), with \(\tau=0.5\). This cutoff is a policy choice: reducing it generally increases positive calls and recall while potentially reducing precision. Choose a production cutoff using validation data and the costs of false positives and false negatives. Logistic regression is fit without class weighting so its probability estimates are not shifted by a class-weight correction; this alone does not guarantee probability calibration. The held-out metrics here are pedagogical estimates, not guarantees for future traffic. The synthetic data encode a simple artificial relationship and do not establish real customer behavior.

## Training and serving skew

The API uses the same serialized preprocessing pipeline as training, which prevents common mismatches such as scaling with one set of means in the notebook and another in the service. Schema checks also reject missing and unexpected training columns; request validation restricts feature ranges and contract labels. These measures do not detect every shift. Monitor feature distributions, missingness, prediction rates, and eventual outcomes. Compare live inputs to the training population and retrain only after investigating drift and label quality.

Covariate shift is the assumption that the feature distribution \(P(X)\) changes while the conditional relationship \(P(Y\mid X)\) remains stable. Under that assumption, predictions may still be useful, though high shift can leave parts of the new population poorly represented. If the relationship between features and churn changes, covariate-shift corrections do not solve the problem. Monitoring inputs can reveal distribution changes; outcome labels are needed to assess whether predictive quality changed.

## Statistical estimator and software contract

Statistically, a learning procedure maps a sample \(D\) to an estimated parameter set \(\hat\theta\), and the fitted model maps a feature vector to a probability. In software, the service has a separate contract: which fields a request must contain, their types and allowed values, what a response contains, and which errors callers can expect. A mathematically valid model can still be unusable if those input and output rules are unclear or change silently.

Reloading a saved artifact should preserve predictions for the same inputs in a compatible software environment; the round-trip test checks this property. Reproducing a fit is a stronger claim. It also requires the same data bytes, preprocessing and split rules, random seeds, package versions, and compatible numerical behavior. Even then, compare floating-point results with a tolerance when platforms or numerical libraries differ.

## Security and operational boundaries

The API accepts a small validated JSON record and has no authentication, authorization, rate limiting, TLS configuration, audit logging, or privacy controls. It is a local teaching service and must not receive real customer data or be exposed publicly as-is. `joblib` uses Python pickle semantics: load artifacts only from a trusted source, since a malicious artifact can execute code. In a real deployment, pin dependency versions, authenticate callers, protect transport and stored data, limit request rates, and define monitoring, rollback, and artifact provenance.

## Work through the lesson

Open `lesson.ipynb` to derive the probability model and inspect training, metrics, persistence, and API behavior. Complete the questions in `exercises.ipynb`; check your reasoning against `solutions.ipynb`. The notebooks discover the repository root from their own location and use temporary output paths, so running them does not overwrite the shared model artifact. They use FastAPI's in-process `TestClient` rather than starting a blocking server.

To build the container from the repository root and publish its API only on the local machine:

```console
docker build -t churn-course-api .
docker run --rm -p 127.0.0.1:8001:8000 churn-course-api
```

The root Dockerfile installs the course package, trains on the bundled synthetic `data/churn.csv`, and starts Uvicorn. Check `http://127.0.0.1:8001/health` and send prediction requests to `http://127.0.0.1:8001/predict`. The container listens on all interfaces internally; the host port mapping above exposes it only through loopback.
