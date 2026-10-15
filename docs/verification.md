# Verification record

Verified on 2026-10-14 using Windows and Python 3.12.10 in the repository's `.venv`. Exact installed dependencies are recorded in `requirements-lock.txt`; this lock is a Windows classroom snapshot. Use the compatible ranges in `pyproject.toml` for other platforms.

- All 24 notebooks executed successfully in separate kernels: lessons, exercises, and solutions for lectures 01–08. After final revisions, the code cells were compared against the executed copies; all match. Executed copies and generated figures are under ignored `.verification/`.
- All 15 pytest cases passed: persistence/reload parity, API parity and saved threshold, schema rejection, numeric validation, and unavailable/malformed artifacts.
- Training CLI completed with `--track`, recording an MLflow run and a saved pipeline. The final lecture also executes local MLflow tracking and queries the resulting run.
- The live Uvicorn service returned a successful health response and prediction over local HTTP.
- All seven CSV datasets reproduced byte-for-byte from their generators without overwriting the classroom fixtures. The extra four datasets use independent generators for fraud/customer geometry, authored support tickets, and chronological sales.
- The website built successfully. All 41 HTML pages passed local link/download checks. Browser checks confirmed the topic filter, the eight-lecture sequence, previous/next navigation, and MathJax rendering. A website preview is saved in `course-preview.png`.
- Forecasting feature checks verify that perturbing future observations cannot alter earlier forecast features. Text splits keep every related template family in a single partition; clustering excludes latent generator labels from fitting and selection.
- `pip check` reported no broken requirements.

Limitations: the Docker engine was stopped, so the image was not built or run. GitHub Actions and Pages workflows are prepared but have not run remotely. No GitHub remote or public hosting was created. MathJax on the website requires an internet connection; notebooks contain the same mathematical exposition for offline study.

Successful notebook execution verifies the supplied scaffolding and solutions, not whether a student has answered the exercise prompts. Synthetic-data results are teaching examples, not a real-world performance validation.
