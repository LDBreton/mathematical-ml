# Lecture 07 — Time-series forecasting

This lecture treats forecasting as prediction from an information set available at a stated origin. It derives the conditional-mean forecast under squared-error loss, constructs autoregressive lag windows without target leakage, and compares a weekly seasonal-naive baseline with XGBoost.

## Learning objectives

After this lecture, you should be able to:

- Explain conditional expectation given a filtration and identify which values are available at a forecast origin.
- Construct lag and rolling-window predictors that use only prior observations.
- Explain why a random iid split does not estimate future forecasting performance.
- Compare a seasonal-naive baseline and a learned model with rolling-origin evaluation.
- Distinguish rolling one-step forecasts with sequential actual updates from fixed-origin multi-day forecasts.
- Interpret MAE, RMSE, prediction timelines, and residual plots in the target's units.

## Mathematical route

For a future response $Y_{t+h}\in L^2$ and forecast $g\in L^2$ measurable with respect to origin information $\mathcal F_t$, the squared-error forecast that minimizes conditional risk is $\mathbb E[Y_{t+h}\mid\mathcal F_t]$. The decomposition

$$\mathbb E[(Y_{t+h}-g)^2\mid\mathcal F_t]=\operatorname{Var}(Y_{t+h}\mid\mathcal F_t)+\left(g-\mathbb E[Y_{t+h}\mid\mathcal F_t]\right)^2$$

shows why a forecast must be measurable with respect to information available at the origin. An autoregressive model approximates this forecast as a function of past observations and known future calendar values. For a one-step forecast, lags $Y_{t-k}$ and a trailing average $\frac1q\sum_{j=1}^qY_{t-j}$ use prior values only. The implementation shifts the target by one before computing rolling means.

Rows are split in date order. The model is trained on the first block, early stopping selects its iteration count on the next block, and the last block is evaluated once. The primary test scenario is rolling one-step-ahead: after each forecast, the actual target is observed and can enter subsequent lag features, while fitted model parameters stay fixed. This is different from a fixed-origin multi-day forecast, which cannot use any actuals from within its forecast horizon and must recursively use predictions or use horizon-specific models.

The lesson also shows expanding-window folds on development data before the final test boundary. Each fold has an expanding training history, an inner contiguous validation block for early stopping, and a later contiguous evaluation block. This is a development diagnostic and never uses the final test dates.

## Files

- `lesson.ipynb` — theory, leakage-free feature construction, model selection, final test comparison, and development backtest.
- `exercises.ipynb` — runnable data and boundary setup with forecasting questions.
- `solutions.ipynb` — complete executable calculations and explanations.
- `../../data/daily_sales.csv` — deterministic synthetic daily series; see [`../../data/sales_dataset.md`](../../data/sales_dataset.md).

## Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\check_notebooks.py --lecture 07_time_series
```

Or start Jupyter from the repository root or this lecture directory and run the notebooks from top to bottom. Their data lookup checks the current directory and parent directories for `data/daily_sales.csv`.

## Limits

The CSV is synthetic and is not evidence about a real business. Weekly and smooth annual patterns are built into the generator, so the weekly seasonal-naive forecast is a natural benchmark. The final scores represent one-day-ahead forecasts issued sequentially with actual lag updates and fixed model parameters; they do not represent a multi-day forecast issued once at a fixed origin. MAE and RMSE are measured in sales units. No percentage metric is needed for this positive-valued example.

The more complex model need not beat seasonal persistence. Tree ensembles make piecewise-constant predictions and can struggle with a drifting level beyond their training range. If the baseline wins, report that result and investigate the validation evidence rather than tuning against the final test.
