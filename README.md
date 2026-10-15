# Machine learning for mathematicians

Four hands-on lectures connecting probability, optimization, and linear algebra to readable Python and a working prediction service. Start with **01 → 02 → 03 → 08**; numbering reserves space for future lectures.

Prerequisites: basic Python functions and arrays, linear algebra, derivatives, conditional probability, and elementary statistics. No prior machine-learning experience is assumed. All datasets are small, synthetic, included locally, and documented in [data/README.md](data/README.md). No accounts, paid APIs, GPU, or downloads of external data are needed.

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
| [08: Deployment](lectures/08_deployment/README.md) | How does a fitted model become a service? | Statistical versus software contracts, reproducibility | Tracked training and a validated prediction API |

For each lecture, read its README, run `lesson.ipynb` in order, attempt `exercises.ipynb`, then compare with `solutions.ipynb`. Exercise notebooks contain runnable scaffolding; successful execution alone does not mean an exercise is answered. Work through the written questions and replace the indicated student work. Plan roughly 2–3 hours per lecture plus exercises.

## Course website

```powershell
python scripts/build_site.py
python -m http.server 8000 --bind 127.0.0.1
```

Open **http://127.0.0.1:8000/site/**. The navigator includes rendered theory and code, lecture instructions, and notebook downloads. Math rendering uses MathJax from a CDN when online; the local notebooks remain the offline mathematics reference. Press Ctrl+C to stop the server. The generated website can be hosted through GitHub Pages using the included manual workflow.

## Verify the course

```powershell
python -m pytest
python scripts/check_notebooks.py
```

The notebook runner executes all lessons, exercises, and solutions using separate kernels and writes results under ignored `.verification/`. It checks execution, not completion of student answers. The committed notebooks keep clean outputs so students generate their own figures.

The latest local checks and their limitations are recorded in [verification.md](docs/verification.md). To validate the website after rebuilding, run `python scripts/check_site.py`.

## Reproducibility and teaching

CSV fixtures are committed. Regenerate them with `python scripts/generate_data.py` only when intentionally updating the classroom inputs. Dependency ranges describe compatible installations; `requirements-lock.txt` records the environment used for verification. For an exact classroom environment install that file before `python -m pip install --no-deps -e .`. Lock versions target the verified Python version and platform; CI additionally checks a fresh installation from declared ranges.

See [instructor guide](docs/instructor-guide.md) for learning outcomes, suggested timing, and assessment. Data models are deliberately simplified. Performance on these fixtures does not establish real-world accuracy, causal effects, fairness, or production readiness. The API is a local teaching service.

This folder is a GitHub-ready source repository. To publish, create an empty GitHub repository, add its remote, and push the local branch. No remote is created or uploaded automatically.

For GitHub Pages, select **GitHub Actions** as the Pages source in repository settings, then manually run **Publish course navigator** under Actions. The workflow builds the `site/` directory and publishes it. The verification workflow runs tests and all notebooks on pushes and pull requests. Select a code/content license before distributing the course publicly.
