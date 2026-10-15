"""Optional expanding-window development diagnostic for lecture 07."""
import pandas as pd

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def rolling_development_backtest(
    data,
    feature_names,
    development_end,
    initial_train_size,
    validation_size,
    test_size,
):
    """Expanding refits; each fold selects rounds on its own inner validation dates."""
    rows = []
    origin = initial_train_size
    fold = 1
    while origin + validation_size + test_size <= development_end:
        training = data.iloc[:origin]
        validation = data.iloc[origin : origin + validation_size]
        evaluation = data.iloc[
            origin + validation_size : origin + validation_size + test_size
        ]
        fold_model = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=400,
            learning_rate=0.04,
            max_depth=3,
            min_child_weight=5,
            reg_lambda=5.0,
            early_stopping_rounds=20,
            eval_metric="rmse",
            random_state=17,
            n_jobs=2,
        )
        fold_model.fit(
            training[feature_names],
            training["sales"],
            eval_set=[(validation[feature_names], validation["sales"])],
            verbose=False,
        )
        predicted = fold_model.predict(evaluation[feature_names])
        actual = evaluation["sales"].to_numpy()
        naive = evaluation["lag_7"].to_numpy()
        rows.append(
            {
                "fold": fold,
                "fit_through": training["date"].max().date(),
                "validation_through": validation["date"].max().date(),
                "evaluation_start": evaluation["date"].min().date(),
                "evaluation_end": evaluation["date"].max().date(),
                "selected_rounds": fold_model.best_iteration + 1,
                "MAE": mean_absolute_error(actual, predicted),
                "RMSE": mean_squared_error(actual, predicted) ** 0.5,
                "seasonal_naive_MAE": mean_absolute_error(actual, naive),
                "seasonal_naive_RMSE": mean_squared_error(actual, naive) ** 0.5,
            }
        )
        fold += 1
        origin += test_size
    return pd.DataFrame(rows)


