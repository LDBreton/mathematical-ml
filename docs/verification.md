# Verification record

## Current course revision

Verified locally on Windows with Python 3.12.10 in the repository environment. Installed versions are recorded in `requirements-lock.txt`; the gallery manifest records the numerical environment for captured outputs.

- The course now contains eight guided lesson notebooks. Separate exercises and solutions are temporarily retired from the source tree, navigation, and download bundle; earlier versions remain in Git history. Each lesson includes expanded software-option explanations and worked examples. All eight current lesson notebooks executed successfully in separate kernels, and exported snapshots match every current source cell.
- All 17 pytest cases passed, including the notebook API helper's environment/cache restoration after an interrupted demonstration.
- Exported 106 actual lesson outputs across eight galleries. Every snapshot is linked to its source cell. Build-time checks compare normalized source and dataset SHA-256 hashes, preventing stale snapshots after edits.
- All 36 generated HTML pages pass checks for local links, section anchors, downloads, and image descriptions. Python and shell source blocks are highlighted at build time using Pygments and a VS Code-inspired Dark+ palette.
- Clustering displays its silhouette-selected model (k=2 in this run), cluster sizes, original-unit profiles, standardized centroid heatmap, PCA projection, and ten-start sensitivity diagnostic. The earlier k=4 picture remains explicitly illustrative.
- Deployment selects its threshold on validation, freezes that fitted pipeline, evaluates the final test once, and saves the exact policy. Assertions verify probability parity before saving, after loading, and through the API, plus threshold/decision parity and invalid-input rejection. MLflow records the same artifact without retraining.
- Classification includes validation reliability bins and confusion counts. Rare-event analysis compares threshold cost and alert workload, with the always-negative test cost in the same table. Text demonstrates sparse counts, IDF, normalization, cosine similarity, sibling groups, and unseen-token behavior. Forecasting checks that changing the contemporaneous target and future outcomes cannot alter its predictors.

## Reproduce the reading-site results

```console
python -m pytest
python scripts/check_notebooks.py
python scripts/export_lesson_results.py
python scripts/build_site.py
python scripts/check_site.py
```

Commit `docs/results/` with the matching teaching-source changes. Pages builds from these committed outputs; the separate verification workflow executes all notebooks afresh. Captured outputs document one successful local run. Numerical values, initialization outcomes, and rendered figures can differ across compatible environments.

## Earlier checks and limits

The CLI trainer, local MLflow tracking, and live Uvicorn health/prediction endpoints were previously exercised. All seven CSV generators reproduced the committed fixtures in the verified local environment. The repository and GitHub Pages site are public, with automatic Pages deployment on pushes to main; workflows have run successfully.

The Docker engine was stopped during initial verification, so an image build/run has not been verified. This revision uses an in-process HTTP client for the deployment notebook. MathJax needs an internet connection; code highlighting and captured figures work without a CDN. Synthetic-data results do not establish real-world accuracy, calibration, causality, or production readiness.
