# Lecture 03 — XGBoost for regression

This lesson develops gradient-boosted trees from functional gradient descent, derives the regularized second-order tree objective, and compares XGBoost with a mean predictor and a random forest on hourly bike-demand scenarios.

## Files

- `lesson.ipynb` — guided theory, implementation, diagnostics, and interpretation.
- `exercises.ipynb` — runnable setup followed by exercises with safe-to-run TODO cells.
- `solutions.ipynb` — complete worked answers to the exercises.

## Data and setup

The notebooks locate `data/bike_demand.csv` by checking the current working directory and its parent directories. Run Jupyter from the repository root or open the notebooks in `lectures/03_xgboost`. The CSV must contain `temperature_c`, `humidity`, `wind_kmh`, `hour`, `weekday`, `season`, and `rentals`.

From the repository root, install the course and its declared dependencies using the setup in the root README:

```powershell
python -m pip install -e .
```

The rows represent independently generated hourly scenarios. They are not observations in a continuous chronological time series. We therefore use a reproducible random train/validation/test split and do not claim that these scores measure forecasting performance on future dates.

The three models receive the same training and held-out test rows. XGBoost uses a separate validation subset of the training partition for early stopping. The test partition is evaluated only after fitting and is never used to choose the number of boosting rounds or tune other settings. XGBoost's `early_stopping_rounds` is passed to `XGBRegressor` at construction, as expected by current XGBoost's scikit-learn API.

## Learning goals

By the end, you should be able to explain stagewise function-space boosting, derive the optimal regularized leaf value and split gain from a second-order Taylor approximation, interpret the regularization controls, and design an evaluation split that keeps model selection separate from final assessment.

The gain formula is a local approximation to the chosen objective. Its interpretation depends on the loss, Hessian weights, regularization convention, and tree constraints. A positive training split gain is not evidence of improved generalization; use held-out validation and test results for that question.
