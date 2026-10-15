# Machine learning for mathematicians

Eight hands-on lectures connecting probability, optimization, linear algebra, and temporal reasoning to readable Python and a working prediction service. Follow **01 → 02 → 03 → 04 → 05 → 06 → 07 → 08**.

Prerequisites: basic Python functions and arrays, linear algebra, derivatives, conditional probability, and elementary statistics. No prior machine-learning experience is assumed. All datasets are small, synthetic, included locally, and documented in [data/README.md](data/README.md). No accounts, paid APIs, GPU, or downloads of external data are needed.

New to machine-learning libraries? Read [Your first experiment](docs/first-steps.md) for vocabulary, array shapes, the estimator API, and a step-by-step notebook walkthrough.

## Setup once

Use Python 3.11 or 3.12. In a terminal opened at the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m ipykernel install --user --name mathematical-ml --display-name "Mathematical ML"
python -m jupyterlab
```

If PowerShell blocks activation, use `.venv\Scripts\python.exe` in place of `python` for every command; activation is optional. On macOS/Linux activate with `source .venv/bin/activate`. In Jupyter select the **Mathematical ML** kernel. All later terminal commands assume this environment.

## Study route

| Lecture | Question | Mathematical foundation | Practical output |
|---|---|---|---|
| [01: Regression](lectures/01_regression/README.md) | How do we estimate house prices? | Empirical risk, least squares, regularization | A preprocessing and regression pipeline |
| [02: Classification](lectures/02_classification/README.md) | Who may leave a service? | Bernoulli likelihood, logistic regression, decision costs | Probabilities and a defensible threshold |
| [03: XGBoost](lectures/03_xgboost/README.md) | Can trees capture nonlinear demand? | Additive models, functional gradients, second-order tree objectives | A baseline-controlled boosting experiment |
| [04: Imbalanced learning](lectures/04_imbalanced_learning/README.md) | How do we detect rare fraud? | Prevalence, precision–recall, weighted risk, decision costs | A validation-selected alert policy |
| [05: Text classification](lectures/05_text_classification/README.md) | How do we route support messages? | Sparse TF-IDF vectors, cosine geometry, multinomial likelihood | A text classification pipeline evaluated by template family |
| [06: Clustering](lectures/06_clustering/README.md) | How do we segment customers without labels? | K-means minimization, PCA, internal validation | Interpretable clusters and stability diagnostics |
| [07: Time-series forecasting](lectures/07_time_series/README.md) | How do we forecast tomorrow's sales? | Information sets, lagged features, rolling-origin evaluation | Seasonal baseline and XGBoost one-step forecasts |
| [08: Deployment](lectures/08_deployment/README.md) | How does a fitted model become a service? | Statistical versus software contracts, reproducibility | Tracked training and a validated prediction API |

For each lecture, read its README, run `lesson.ipynb` in order, attempt `exercises.ipynb`, then compare with `solutions.ipynb`. Exercise notebooks contain runnable scaffolding; successful execution alone does not mean an exercise is answered. Work through the written questions and replace the indicated student work. Plan roughly 2–3 hours per lecture plus exercises.

## Course website

```powershell
python scripts/build_site.py
python -m http.server 8000 --bind 127.0.0.1
```

Open **http://127.0.0.1:8000/site/**. The navigator includes rendered theory and code, lecture instructions, and notebook downloads. Math rendering uses MathJax from a CDN when online; the local notebooks remain the offline mathematics reference. Press Ctrl+C to stop the server. The generated website can be hosted through GitHub Pages using the included GitHub Actions workflow.

## Verify the course

```powershell
python -m pytest
python scripts/check_notebooks.py
```

The notebook runner executes all lessons, exercises, and solutions using separate kernels and writes results under ignored `.verification/`. It checks execution, not completion of student answers. The committed notebooks keep clean outputs so students generate their own figures.

The latest local checks and their limitations are recorded in [verification.md](docs/verification.md). To validate the website after rebuilding, run `python scripts/check_site.py`.

Run `python scripts/check_data.py` to check that the generators reproduce the committed CSV bytes in the current environment without overwriting them. Exact byte reproduction is a stronger condition than statistical equivalence and may depend on numerical-library versions.

## Reproducibility and teaching

CSV fixtures are committed. Regenerate all fixtures with `python scripts/generate_all_data.py` only when intentionally updating the classroom inputs. `generate_data.py` regenerates the original housing, churn, and bike data; the extension generators can be run separately. Each dataset has its own documented sampling model. Dependency ranges describe compatible installations; `requirements-lock.txt` records the environment used for verification. For an exact classroom environment install that file before `python -m pip install --no-deps -e .`. Lock versions target the verified Python version and platform; CI additionally checks a fresh installation from declared ranges.

Lectures 04–07 add no dependencies. Text classification uses local sparse TF-IDF features; pretrained embeddings are discussed without requiring model downloads. Forecasting uses genuine chronological data and explicitly evaluates rolling one-step predictions, unlike the independent hourly scenarios in lecture 03.

See [instructor guide](docs/instructor-guide.md) for learning outcomes, suggested timing, and assessment. Data models are deliberately simplified. Performance on these fixtures does not establish real-world accuracy, causal effects, fairness, or production readiness. The API is a local teaching service.

Finish with the [course project](docs/course-project.md), which asks you to justify a complete experiment and an optional software handoff. The deployment API serves churn specifically; other tasks require their own input contract.

## Website and repository

- [Browse the course](https://ldbreton.github.io/mathematical-ml/)
- [Source repository](https://github.com/LDBreton/mathematical-ml)

GitHub Pages uses **GitHub Actions** as its publishing source. Pushes to `main`
automatically build and publish the navigator. You can also run **Publish course
navigator** manually under Actions. The separate **Verify course** workflow runs
tests and all notebooks on pushes and pull requests.

To publish a fork, enable Pages in **Settings → Pages → Build and deployment**,
choose **GitHub Actions**, and run **Publish course navigator**. Relative site links
work under your repository's subpath without changes. Update these public links
for your fork.

GitHub Pages serves the documentation and downloads. Run notebooks and the
lecture 08 Python API locally; Pages does not run Python servers.
